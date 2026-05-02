"""
decision_consistency.py — Decision Consistency Engine (WO-002)
같은 입력에 대해 일관된 intent_class를 반환하는 규칙 기반 엔진.
Ollama 호출 금지. HTTP 금지. Python 규칙만.

흐름:
    BrainRequest.input_text
        → 키워드 기반 intent_class 추정
        → consistency_score 계산 (WO-002: 규칙 기반 고정값)
        → ConsistencyResult
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict

from backend.vian_brain_kernel.contracts import BrainRequest

# 키워드 → intent_class 매핑 (WO-003에서 Ollama로 교체 가능)
_INTENT_MAP: Dict[str, str] = {
    "안녕": "greeting",
    "hello": "greeting",
    "hi": "greeting",
    "요약": "summarize",
    "찾": "search",
    "저장": "save",
    "삭제": "delete",
    "실행": "execute",
    "도움": "help",
    "help": "help",
}


@dataclass
class ConsistencyResult:
    intent_class: str = "unknown"
    consistency_score: float = 0.5
    guard_required: bool = False


class DecisionConsistencyEngine:
    """
    규칙 기반 Intent 분류 + Consistency Score 계산.

    WO-003에서 Ollama 연동으로 교체될 예정.
    지금은 키워드 매핑으로 intent_class를 추정합니다.
    """

    def run(self, req: BrainRequest) -> ConsistencyResult:
        text = req.input_text.lower()
        intent = "unknown"
        for keyword, intent_class in _INTENT_MAP.items():
            if keyword in text:
                intent = intent_class
                break

        # 위험 intent 감지
        guard_required = intent in ("delete", "execute")

        # WO-002: consistency_score는 규칙 신뢰도 고정값
        # WO-003+에서 실제 fingerprint DB 비교로 교체
        score = 0.8 if intent != "unknown" else 0.4

        return ConsistencyResult(
            intent_class=intent,
            consistency_score=score,
            guard_required=guard_required,
        )
