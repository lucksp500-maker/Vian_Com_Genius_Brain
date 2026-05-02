"""
InternalConfidenceModel — WO-005
Guard 이전에 Genius가 스스로 위험도와 확신도를 판단합니다.
Guard는 최후의 안전망 — Confidence는 Guard 전 자체 1차 판단입니다.

흐름:
    intent_class + risk_class + memory_match + ground_truth
    → confidence_score (0.0~1.0) + stop_or_continue + needs_human_approval
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# [의존성] 연결: commandos_brain_router.py / 단독 수정 금지

# Ground Truth Seed 원칙 (설계도 섹션 H 기반)
_GROUND_TRUTH_DENY: set[str] = {
    "delete", "삭제", "제거",                     # 삭제 기본 금지
    "external_send", "외부전송", "send_external",  # 외부 전송 기본 금지
    "form_submit", "폼제출",                       # 폼 제출 기본 금지
}


@dataclass
class ConfidenceAssessment:
    """
    Internal Confidence Model 출력.

    confidence_score: 0.0(완전 불확실) ~ 1.0(완전 확신)
    stop_or_continue: "continue" | "stop" | "ask"
    needs_human_approval: True이면 사용자 승인 필수
    uncertainty_reason: 불확실성 원인 (있으면)
    ground_truth_conflict: Ground Truth Seed와 충돌 여부
    """
    confidence_score: float
    stop_or_continue: str       # "continue" | "stop" | "ask"
    needs_human_approval: bool
    uncertainty_reason: Optional[str]
    ground_truth_conflict: bool


def assess_confidence(
    intent_class: str,
    risk_class: str,
    memory_match_score: float = 0.0,
    memory_conflict: bool = False,
    consistency_score: float = 1.0,
    cold_start: bool = False,
) -> ConfidenceAssessment:
    """
    내부 확신도를 계산합니다.

    Ground Truth Seed 원칙:
    - 삭제/외부전송/폼제출 intent → 항상 stop + needs_human_approval
    - risk=high → needs_human_approval
    - risk=none + 일관성 높음 → 자체 판단 가능
    - cold_start (기억 없음) → 낮은 confidence, ask
    """
    intent_lower = intent_class.lower()

    # Ground Truth Seed 충돌 확인
    ground_truth_conflict = any(deny in intent_lower for deny in _GROUND_TRUTH_DENY)
    if ground_truth_conflict:
        return ConfidenceAssessment(
            confidence_score=0.1,
            stop_or_continue="stop",
            needs_human_approval=True,
            uncertainty_reason="Ground Truth Seed: 해당 작업은 기본 금지 원칙에 해당합니다.",
            ground_truth_conflict=True,
        )

    # risk 기반 기본 판단
    if risk_class == "high":
        return ConfidenceAssessment(
            confidence_score=0.3,
            stop_or_continue="ask",
            needs_human_approval=True,
            uncertainty_reason="위험도 높음 — 사용자 승인 필요",
            ground_truth_conflict=False,
        )

    if risk_class == "medium":
        base_score = 0.55
        if memory_conflict:
            base_score -= 0.15
        if cold_start:
            base_score -= 0.1
        final_score = max(0.2, min(0.75, base_score + consistency_score * 0.1))
        return ConfidenceAssessment(
            confidence_score=final_score,
            stop_or_continue="ask",
            needs_human_approval=True,
            uncertainty_reason="위험도 중간 — 확인 권장",
            ground_truth_conflict=False,
        )

    # risk=low or none
    base_score = 0.80 if risk_class == "none" else 0.65
    if memory_conflict:
        base_score -= 0.2
        stop = "ask"
        approval = True
        reason: Optional[str] = "이전 유사 작업에서 실패/거절 기록 있음"
    else:
        stop = "continue"
        approval = False
        reason = None

    if cold_start:
        base_score -= 0.1
        if stop == "continue":
            stop = "ask"
            approval = True
            reason = "첫 번째 실행 — 이전 기록 없음, 확인 권장"

    if memory_match_score > 0.5:
        base_score = min(1.0, base_score + 0.1)

    final_score = max(0.0, min(1.0, base_score + consistency_score * 0.05))

    return ConfidenceAssessment(
        confidence_score=round(final_score, 3),
        stop_or_continue=stop,
        needs_human_approval=approval,
        uncertainty_reason=reason,
        ground_truth_conflict=False,
    )
