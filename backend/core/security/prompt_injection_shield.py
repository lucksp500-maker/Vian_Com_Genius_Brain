"""
PromptInjectionShield — WO-007
웹 페이지 원문에 포함된 "명령 주입" 패턴을 탐지합니다.
페이지 본문이 시스템 명령으로 승격되는 것을 차단합니다.

원칙:
    웹 페이지 원문은 신뢰할 수 없는 입력입니다.
    LLM 또는 파서에 전달하기 전 반드시 이 Shield를 통과해야 합니다.

감지 패턴 유형:
    1. 지시 무시 패턴  — "이전 지시 무시", "ignore previous instructions"
    2. 역할 전환 패턴  — "당신은 이제", "you are now", "act as"
    3. 시스템 탈출 패턴 — "system:", "SYSTEM PROMPT", "DAN mode"
    4. 권한 상승 패턴  — "관리자 권한", "sudo", "as root"
    5. 숨겨진 텍스트   — 제로폭 문자, 비가시 유니코드 남용

[보호] 이유: 보안 핵심 모듈 / 수정 필요 시: _PATTERNS 목록만 추가
[의존성] 연결: browser_automation_adapter.process() / 단독 수정 금지
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Optional


# ─── 주입 패턴 목록 ──────────────────────────────────────────────

# 각 항목: (패턴_이름, 정규표현식, 설명)
_PATTERNS: list[tuple[str, str, str]] = [
    # 한국어 지시 무시
    ("ignore_prev_ko",    r"이전\s*지시\s*(무시|삭제|잊어)",             "이전 지시 무시 (한국어)"),
    ("ignore_prev_ko2",   r"앞의\s*명령\s*(무시|삭제)",                   "앞의 명령 무시 (한국어)"),
    ("new_instruction_ko",r"새로운\s*(지시|명령|역할)",                    "새 지시 주입 (한국어)"),
    # 영어 지시 무시
    ("ignore_prev_en",    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions?|rules?|prompts?)",
                                                                          "ignore previous instructions"),
    ("disregard_en",      r"disregard\s+(all\s+)?(previous|prior|your)\s+\w+", "disregard prior"),
    ("forget_en",         r"forget\s+(everything|all|your\s+instructions?)", "forget instructions"),
    # 역할 전환
    ("role_switch_ko",    r"당신은\s*(이제|지금부터|앞으로)\s*.{0,30}입니다",  "역할 전환 (한국어)"),
    ("role_switch_en",    r"you\s+are\s+now\s+\w+",                       "you are now"),
    ("act_as_en",         r"act\s+as\s+(a\s+)?\w+",                       "act as"),
    ("pretend_en",        r"pretend\s+(you\s+are|to\s+be)",                "pretend to be"),
    # 시스템 탈출
    ("system_prefix",     r"(?i)^system\s*:",                              "system: prefix"),
    ("system_prompt",     r"(?i)system\s*prompt",                          "system prompt reference"),
    ("dan_mode",          r"(?i)DAN\s*mode",                               "DAN mode"),
    ("jailbreak_ko",      r"(?i)(탈옥|잠금\s*해제|제한\s*해제)",           "탈옥/잠금해제 시도"),
    # 권한 상승
    ("sudo_pattern",      r"(?i)\bsudo\b",                                 "sudo command"),
    ("root_escalation",   r"(?i)as\s+(root|admin|administrator)",          "root/admin escalation"),
    ("admin_ko",          r"관리자\s*(권한|모드|계정)",                     "관리자 권한 (한국어)"),
    # 구분자 탈출
    ("delimiter_escape",  r"(---|===|###)\s*(system|assistant|human|user)\s*:",
                                                                          "delimiter injection"),
    ("bracket_escape",    r"<\s*(system|instruction|prompt)\s*>",          "tag injection"),
]

# 사전 컴파일
_COMPILED: list[tuple[str, re.Pattern[str], str]] = [
    (name, re.compile(pattern, re.IGNORECASE | re.MULTILINE), desc)
    for name, pattern, desc in _PATTERNS
]

# 제로폭/비가시 유니코드 문자 탐지 (최소 3개 이상 연속)
_INVISIBLE_RE = re.compile(r"[\u200b\u200c\u200d\u200e\u200f\ufeff\u00ad]{3,}")

# C-06 Fix: Cyrillic 동형이자 → Latin ASCII 매핑 (NFKC는 이 변환 미지원)
# Cyrillic 문자가 Latin과 시각적으로 동일하지만 다른 코드포인트를 가짐
# 예: і(U+0456) ≠ i(U+0069), о(U+043E) ≠ o(U+006F)
_CYRILLIC_HOMOGLYPH_MAP = str.maketrans({
    # Lowercase Cyrillic → Latin
    '\u0430': 'a',  # а → a
    '\u0435': 'e',  # е → e
    '\u043e': 'o',  # о → o
    '\u0440': 'p',  # р → p
    '\u0441': 'c',  # с → c
    '\u0445': 'x',  # х → x
    '\u0456': 'i',  # і → i (Byelorussian-Ukrainian I)
    # Uppercase Cyrillic → Latin
    '\u0410': 'A',  # А → A
    '\u0412': 'B',  # В → B
    '\u0415': 'E',  # Е → E
    '\u041a': 'K',  # К → K
    '\u041c': 'M',  # М → M
    '\u041d': 'H',  # Н → H
    '\u041e': 'O',  # О → O
    '\u0420': 'P',  # Р → P
    '\u0421': 'C',  # С → C
    '\u0422': 'T',  # Т → T
    '\u0425': 'X',  # Х → X
})


# ─── 결과 타입 ──────────────────────────────────────────────────

@dataclass
class ScanResult:
    """
    PromptInjectionShield.scan() 반환값.

    injection_detected: True = 차단 필요
    matched_patterns:   감지된 패턴 이름 목록
    risk_score:         0.0 ~ 1.0 (1.0 = 즉시 차단)
    cleaned_content:    주입 의심 구절이 제거된 텍스트 (참조용)
    """
    injection_detected: bool
    matched_patterns: list[str] = field(default_factory=list)
    risk_score: float = 0.0
    pattern_descriptions: list[str] = field(default_factory=list)
    cleaned_content: Optional[str] = None


# ─── Shield 클래스 ──────────────────────────────────────────────

class PromptInjectionShield:
    """
    웹 페이지 원문 Prompt Injection 탐지기.

    사용법:
        shield = PromptInjectionShield()
        result = shield.scan(page_content)
        if result.injection_detected:
            # 처리 중단 또는 사용자에게 경고
    """

    # 단일 패턴 감지 시 즉시 차단 (risk_score=1.0)
    _BLOCK_THRESHOLD = 1

    def scan(self, content: str) -> ScanResult:
        """
        텍스트에서 Prompt Injection 패턴을 탐지합니다.

        처리 단계:
        1. 길이 0 입력 → clean
        2. 비가시 문자 클러스터 탐지
        3. 패턴 목록 순회
        4. 1개 이상 감지 시 injection_detected=True
        """
        if not content or not content.strip():
            return ScanResult(injection_detected=False, risk_score=0.0)

        matched_names: list[str] = []
        matched_descs: list[str] = []

        # C-06 Fix: NFKC 정규화 + Cyrillic 동형이자 매핑
        # NFKC: 전각문자 등 호환 변환 처리
        # translate: і→i, о→o, е→e 등 Cyrillic 시각적 동형 → Latin ASCII 변환
        normalized = unicodedata.normalize("NFKC", content).translate(_CYRILLIC_HOMOGLYPH_MAP)

        # 비가시 문자 탐지 (정규화된 텍스트 기준)
        if _INVISIBLE_RE.search(normalized):
            matched_names.append("invisible_chars")
            matched_descs.append("비가시 유니코드 문자 클러스터 (숨겨진 텍스트 의심)")

        # 정규표현식 패턴 탐지 (NFKC 정규화된 텍스트로 탐지 — homoglyph 우회 차단)
        for name, pattern, desc in _COMPILED:
            if pattern.search(normalized):
                matched_names.append(name)
                matched_descs.append(desc)

        detected = len(matched_names) >= self._BLOCK_THRESHOLD
        risk = min(1.0, len(matched_names) * 0.25)

        # 감지된 패턴 구절 제거 (cleaned version, 참조용)
        cleaned = self._strip_patterns(content, matched_names) if detected else content

        return ScanResult(
            injection_detected=detected,
            matched_patterns=matched_names,
            risk_score=risk,
            pattern_descriptions=matched_descs,
            cleaned_content=cleaned,
        )

    @staticmethod
    def _strip_patterns(content: str, matched_names: list[str]) -> str:
        """감지된 패턴과 일치하는 줄을 [BLOCKED] 로 대체합니다 (참조용)."""
        lines = content.splitlines()
        result_lines = []
        for line in lines:
            blocked = False
            for name, pattern, _ in _COMPILED:
                if name in matched_names and pattern.search(line):
                    result_lines.append("[BLOCKED]")
                    blocked = True
                    break
            if not blocked:
                result_lines.append(line)
        return "\n".join(result_lines)
