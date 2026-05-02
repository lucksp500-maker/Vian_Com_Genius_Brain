"""
pattern_abstraction.py — Pattern Abstraction Engine (WO-002)
반복 입력에서 규칙 후보를 생성하는 엔진.
WO-002: 세션 내 빈도 카운팅만. Pattern Memory 연동은 WO-004+.

흐름:
    BrainRequest.input_text
        → 세션 내 빈도 카운팅
        → 임계값(3회) 초과 시 pattern_candidate 생성
        → PatternResult
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from backend.vian_brain_kernel.contracts import BrainRequest

# [임시] 세션 내 입력 빈도 카운터 — WO-004에서 Pattern Memory로 교체
_frequency: Dict[str, int] = {}
_PATTERN_THRESHOLD = 3


@dataclass
class PatternResult:
    pattern_candidate: Optional[str] = None


class PatternAbstractionEngine:
    """
    반복 입력에서 규칙 후보를 추출합니다.

    WO-002: 세션 내 단순 빈도 카운팅.
    WO-004+에서 Pattern Memory DB와 연동.
    """

    def run(self, req: BrainRequest) -> PatternResult:
        key = req.input_text[:40].lower().strip()
        _frequency[key] = _frequency.get(key, 0) + 1

        candidate = None
        if _frequency[key] >= _PATTERN_THRESHOLD:
            candidate = f"rule_candidate:{key}:freq={_frequency[key]}"

        return PatternResult(pattern_candidate=candidate)
