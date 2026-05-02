"""
AI Intent Bridge — WO-002
Ollama qwen2.5:1.5b를 사용해 자연어 입력을 ActionSpec 후보로 변환합니다.
Ollama 실패 시 regex fallback으로 기본 분류합니다.
"""
from __future__ import annotations

import json
import re
from typing import Optional

import httpx

from backend.core.commandos.action_spec import (
    ActionSpec,
    ActionSource,
    ExecutionState,
    RiskLevel,
    TargetType,
)
from backend.core.commandos.intent_prompt_templates import build_ollama_payload

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "qwen2.5:1.5b"
OLLAMA_TIMEOUT = 10.0  # seconds

# regex fallback 패턴 — Vian_CommandOS regex-fallback-parser.ts 기반 Python 포팅
_REGEX_RULES: list[dict] = [
    {
        "patterns": [r"삭제|delete|제거|지워|지우"],
        "target_type": TargetType.file,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
        "intent_template": "파일 또는 항목을 삭제합니다",
    },
    {
        "patterns": [r"외부.*전송|send.*external|전송|보내|share"],
        "target_type": TargetType.url,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
        "intent_template": "데이터를 외부로 전송합니다",
    },
    {
        "patterns": [r"폼.*작성|form.*fill|자동.*작성|양식.*작성"],
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
        "intent_template": "웹 폼을 자동 작성합니다",
    },
    {
        "patterns": [r"폼.*제출|submit.*form|제출"],
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
        "intent_template": "웹 폼을 제출합니다",
    },
    {
        "patterns": [r"저장|아카이브|archive|save|보관|탭.*저장|현재.*탭"],
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.low,
        "requires_approval": False,
        "intent_template": "현재 탭을 아카이브에 저장합니다",
    },
    {
        "patterns": [r"요약|summarize|summary|정리|요약해"],
        "target_type": TargetType.file,
        "risk_level": RiskLevel.none,
        "requires_approval": False,
        "intent_template": "문서 또는 페이지를 요약합니다",
    },
    {
        "patterns": [r"번역|translate|translation"],
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.none,
        "requires_approval": False,
        "intent_template": "페이지 또는 텍스트를 번역합니다",
    },
    {
        "patterns": [r"찾|검색|search|find|어디|최근"],
        "target_type": TargetType.file,
        "risk_level": RiskLevel.none,
        "requires_approval": False,
        "intent_template": "파일 또는 문서를 검색합니다",
    },
    {
        "patterns": [r"교정|proofread|맞춤법|오타"],
        "target_type": TargetType.text,
        "risk_level": RiskLevel.none,
        "requires_approval": False,
        "intent_template": "텍스트를 교정합니다",
    },
    {
        "patterns": [r"감사.*로그|audit|이력|history|로그.*보여"],
        "target_type": TargetType.system,
        "risk_level": RiskLevel.none,
        "requires_approval": False,
        "intent_template": "감사 로그를 표시합니다",
    },
    {
        "patterns": [r"목록|list|보여|방문|visited"],
        "target_type": TargetType.system,
        "risk_level": RiskLevel.none,
        "requires_approval": False,
        "intent_template": "항목 목록을 표시합니다",
    },
]


def _regex_fallback(raw_input: str) -> dict:
    """regex 기반 fallback 분류. ActionSpec 필드 dict 반환."""
    lower = raw_input.lower()
    for rule in _REGEX_RULES:
        if any(re.search(p, lower) for p in rule["patterns"]):
            return {
                "intent": rule["intent_template"],
                "target_type": rule["target_type"],
                "risk_level": rule["risk_level"],
                "requires_approval": rule["requires_approval"],
                "target_ref": None,
            }
    return {
        "intent": f"명령 의도 파악 불가: {raw_input[:50]}",
        "target_type": TargetType.unknown,
        "risk_level": RiskLevel.medium,
        "requires_approval": True,
        "target_ref": None,
    }


def _parse_ollama_response(response_text: str) -> Optional[dict]:
    """Ollama 응답 텍스트에서 JSON 추출. 실패 시 None."""
    text = response_text.strip()
    # 코드 블록 제거
    text = re.sub(r"```(?:json)?\s*", "", text).strip()
    # JSON 오브젝트 추출
    match = re.search(r"\{[^{}]+\}", text, re.DOTALL)
    if not match:
        return None
    try:
        data = json.loads(match.group())
    except json.JSONDecodeError:
        return None

    required = {"intent", "target_type", "risk_level", "requires_approval"}
    if not required.issubset(data.keys()):
        return None

    # 유효한 enum 값인지 확인
    valid_target = {t.value for t in TargetType}
    valid_risk = {r.value for r in RiskLevel}
    if data.get("target_type") not in valid_target:
        return None
    if data.get("risk_level") not in valid_risk:
        return None

    return data


async def parse_intent(
    raw_input: str,
    source: ActionSource = ActionSource.hud,
    ollama_base_url: str = OLLAMA_BASE_URL,
    ollama_model: str = OLLAMA_MODEL,
) -> ActionSpec:
    """
    자연어 입력을 ActionSpec으로 변환합니다.
    1차: Ollama qwen2.5:1.5b
    2차: regex fallback
    """
    if not raw_input.strip():
        return ActionSpec(
            raw_input=raw_input,
            source=source,
            intent="빈 입력",
            target_type=TargetType.unknown,
            risk_level=RiskLevel.medium,
            requires_approval=True,
        )

    parsed: Optional[dict] = None

    # 1차: Ollama
    try:
        payload = build_ollama_payload(raw_input, ollama_model)
        async with httpx.AsyncClient(timeout=OLLAMA_TIMEOUT) as client:
            resp = await client.post(f"{ollama_base_url}/api/generate", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                response_text = data.get("response", "")
                parsed = _parse_ollama_response(response_text)
    except (httpx.HTTPError, httpx.TimeoutException, Exception):
        parsed = None

    # 2차: regex fallback
    if parsed is None:
        parsed = _regex_fallback(raw_input)

    return ActionSpec(
        raw_input=raw_input,
        source=source,
        intent=parsed.get("intent", ""),
        target_type=parsed.get("target_type", TargetType.unknown),
        risk_level=parsed.get("risk_level", RiskLevel.medium),
        target_ref=parsed.get("target_ref"),
        requires_approval=parsed.get("requires_approval", True),
        preview_required=True,
        execution_state=ExecutionState.pending,
    )
