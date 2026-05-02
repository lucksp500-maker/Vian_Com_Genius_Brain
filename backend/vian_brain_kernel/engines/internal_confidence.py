"""
internal_confidence.py — Internal Confidence Engine (WO-002)
자기정지 여부를 판단하는 신뢰도 모델.
불확실하면 confidence_score가 낮아지고 guard_required가 올라갑니다.

흐름:
    BrainRequest + ConsistencyResult
        → risk_class 결정 (위험 키워드 감지)
        → confidence_score 계산
        → ConfidenceResult
"""
from __future__ import annotations

from dataclasses import dataclass

from backend.vian_brain_kernel.contracts import BrainRequest

_HIGH_RISK_KEYWORDS = {"삭제", "delete", "remove", "실행", "execute", "전송", "send", "결제"}
_MEDIUM_RISK_KEYWORDS = {"저장", "save", "수정", "edit", "업로드", "upload"}


@dataclass
class ConfidenceResult:
    confidence_score: float = 0.5
    risk_class: str = "low"
    approval_required: bool = False


class InternalConfidenceEngine:
    """
    입력 텍스트와 컨텍스트를 기반으로 신뢰도와 위험 등급을 계산합니다.

    Ground Truth 원칙:
    - 삭제/전송/결제 → risk_class=high, approval_required=True
    - 불확실한 입력 → confidence_score < 0.5
    """

    def run(self, req: BrainRequest) -> ConfidenceResult:
        text = req.input_text.lower()
        words = set(text.split()) | set(text)

        # 위험도 분류
        if any(kw in text for kw in _HIGH_RISK_KEYWORDS):
            risk_class = "high"
            confidence_score = 0.3
            approval_required = True
        elif any(kw in text for kw in _MEDIUM_RISK_KEYWORDS):
            risk_class = "medium"
            confidence_score = 0.6
            approval_required = False
        else:
            risk_class = "low"
            confidence_score = 0.85
            approval_required = False

        # risk_hint 반영 (상위 레이어 힌트 우선)
        if req.risk_hint == "high":
            risk_class = "high"
            confidence_score = min(confidence_score, 0.4)
            approval_required = True

        return ConfidenceResult(
            confidence_score=confidence_score,
            risk_class=risk_class,
            approval_required=approval_required,
        )
