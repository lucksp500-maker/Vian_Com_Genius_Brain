"""
CommandosBrainRouter — WO-005
ActionSpec을 4개 뇌 엔진에 통과시켜 consistency/memory/confidence 점수를 채웁니다.
guard/evaluate 엔드포인트에서 Guard 판정 전 호출됩니다.

흐름:
    ActionSpec (pending)
      → DecisionConsistencyEngine → consistency_score 채움
      → SelfReferenceMemoryEngine → memory_citation 채움
      → InternalConfidenceModel    → confidence_score 채움
      → PatternAbstractionEngine   → (이미 기록된 parenting events 기반, 여기서는 평가만)
      → 강화된 ActionSpec 반환

[의존성] 연결: guard_router.py evaluate_action() / 단독 수정 금지
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from backend.core.brain.decision_consistency import DecisionConsistencyEngine, ConsistencyResult
from backend.core.brain.self_reference_memory import SelfReferenceMemoryEngine, MemoryCitation
from backend.core.brain.internal_confidence import ConfidenceAssessment, assess_confidence
from backend.core.commandos.action_spec import ActionSpec


@dataclass
class BrainRouterResult:
    """
    Brain Router 출력 — 4개 뇌 엔진 결과 통합.

    ActionSpec에 이 결과를 병합하여 Guard로 전달합니다.
    """
    consistency: ConsistencyResult
    memory: MemoryCitation
    confidence: ConfidenceAssessment
    enriched_spec: ActionSpec   # confidence_score가 채워진 ActionSpec


# 싱글턴 엔진 인스턴스 (앱 수명 공유)
_consistency_engine = DecisionConsistencyEngine()
_memory_engine = SelfReferenceMemoryEngine()


async def route(spec: ActionSpec) -> BrainRouterResult:
    """
    ActionSpec을 4-Brain Core에 통과시킵니다.

    실패 허용 원칙:
    - 각 엔진이 실패해도 Guard는 정상 진행됩니다.
    - 실패 시 기본값(confidence=0.5, cold_start=True)으로 계속합니다.
    """
    # 1. Decision Consistency
    try:
        consistency = await _consistency_engine.check(spec)
    except Exception:
        from backend.core.brain.decision_consistency import ConsistencyResult
        import hashlib
        consistency = ConsistencyResult(
            fingerprint_id="fallback",
            input_hash=hashlib.sha256(spec.raw_input.encode()).hexdigest()[:16],
            intent_class=spec.intent or "unknown",
            risk_class=str(spec.risk_level),
            consistency_score=0.5,
            repeat_count=1,
            conflict_detected=False,
            recommended_action="ask",
        )

    # 2. Self-Reference Memory
    try:
        memory = await _memory_engine.cite(spec)
    except Exception:
        from backend.core.brain.self_reference_memory import MemoryCitation
        memory = MemoryCitation(
            prior_event_id=None, prior_intent_class=None,
            prior_execution_state=None, memory_weight=0.0,
            memory_conflict=False, lesson=None, cold_start=True,
        )

    # 3. Internal Confidence
    try:
        confidence = assess_confidence(
            intent_class=spec.intent or "unknown",
            risk_class=str(spec.risk_level),
            memory_match_score=memory.memory_weight,
            memory_conflict=memory.memory_conflict,
            consistency_score=consistency.consistency_score,
            cold_start=memory.cold_start,
        )
    except Exception:
        from backend.core.brain.internal_confidence import ConfidenceAssessment
        confidence = ConfidenceAssessment(
            confidence_score=0.5,
            stop_or_continue="ask",
            needs_human_approval=True,
            uncertainty_reason="Brain Router 오류 — 기본값 사용",
            ground_truth_conflict=False,
        )

    # ActionSpec에 confidence_score 주입
    enriched = spec.model_copy(update={"confidence_score": confidence.confidence_score})

    return BrainRouterResult(
        consistency=consistency,
        memory=memory,
        confidence=confidence,
        enriched_spec=enriched,
    )
