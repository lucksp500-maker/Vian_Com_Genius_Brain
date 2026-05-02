"""
kernel.py — VianBrainKernel (WO-002)
4-Brain Core를 하나의 process()로 묶는 독립 두뇌 SDK.

흐름:
    BrainRequest
        ├─► DecisionConsistencyEngine  → intent_class, consistency_score
        ├─► SelfReferenceMemoryEngine  → memory_citation, lesson_candidate
        ├─► InternalConfidenceEngine   → confidence_score, risk_class
        └─► PatternAbstractionEngine   → pattern_candidate
                    │
                    ▼
              BrainResult(brain_mode='kernel', ...)

엔진 fallback 원칙:
    각 엔진이 예외를 던져도 process()는 계속 실행된다.
    실패한 엔진의 결과는 기본값으로 대체된다.

[의존성] GENIUS_BRAIN_CONNECTION_SPEC.md 기준
[주의] HTTP 호출 금지 / Ollama 호출 금지 (WO-003 대상)
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from backend.vian_brain_kernel.contracts import BrainRequest, BrainResult
from backend.vian_brain_kernel.engines.decision_consistency import (
    ConsistencyResult,
    DecisionConsistencyEngine,
)
from backend.vian_brain_kernel.engines.internal_confidence import (
    ConfidenceResult,
    InternalConfidenceEngine,
)
from backend.vian_brain_kernel.engines.pattern_abstraction import (
    PatternAbstractionEngine,
    PatternResult,
)
from backend.vian_brain_kernel.engines.self_reference_memory import (
    MemoryResult,
    SelfReferenceMemoryEngine,
)

logger = logging.getLogger(__name__)

_FALLBACK_CONSISTENCY = ConsistencyResult(
    intent_class="unknown",
    consistency_score=0.0,
    guard_required=False,
)
_FALLBACK_MEMORY = MemoryResult()
_FALLBACK_CONFIDENCE = ConfidenceResult(
    confidence_score=0.0,
    risk_class="low",
    approval_required=False,
)
_FALLBACK_PATTERN = PatternResult()


class VianBrainKernel:
    """
    Vian Brain Kernel — 독립 두뇌 SDK 진입점.

    사용:
        kernel = VianBrainKernel()
        result = kernel.process(BrainRequest(input_text="안녕", ...))
    """

    def __init__(self) -> None:
        self._consistency = DecisionConsistencyEngine()
        self._memory = SelfReferenceMemoryEngine()
        self._confidence = InternalConfidenceEngine()
        self._pattern = PatternAbstractionEngine()

    def process(self, req: BrainRequest) -> BrainResult:
        """
        BrainRequest를 4-Brain Core에 통과시켜 BrainResult를 반환합니다.

        엔진 중 하나가 실패해도 나머지를 계속 실행합니다 (fallback 허용 원칙).
        """
        # 1. Decision Consistency
        try:
            consistency = self._consistency.run(req)
        except Exception as exc:
            logger.warning("DecisionConsistencyEngine failed: %s", exc)
            consistency = _FALLBACK_CONSISTENCY

        # 2. Self-Reference Memory
        try:
            memory = self._memory.run(req)
        except Exception as exc:
            logger.warning("SelfReferenceMemoryEngine failed: %s", exc)
            memory = _FALLBACK_MEMORY

        # 3. Internal Confidence
        try:
            confidence = self._confidence.run(req)
        except Exception as exc:
            logger.warning("InternalConfidenceEngine failed: %s", exc)
            confidence = _FALLBACK_CONFIDENCE

        # 4. Pattern Abstraction
        try:
            pattern = self._pattern.run(req)
        except Exception as exc:
            logger.warning("PatternAbstractionEngine failed: %s", exc)
            pattern = _FALLBACK_PATTERN

        return BrainResult(
            request_id=req.request_id,
            intent_class=consistency.intent_class,
            risk_class=confidence.risk_class,
            confidence_score=confidence.confidence_score,
            consistency_score=consistency.consistency_score,
            memory_citation=memory.memory_citation,
            llm_used=False,
            llm_candidate_response=None,
            brain_final_response=None,
            guard_required=consistency.guard_required,
            approval_required=confidence.approval_required,
            allowed_actions=[],
            blocked_reason=None,
            lesson_candidate=memory.lesson_candidate,
            pattern_candidate=pattern.pattern_candidate,
            brain_mode="kernel",
            fallback_reason=None,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
