"""
Guard Router — WO-002 (WO-005에서 Brain Router 연결)
FastAPI 라우터: ActionSpec → 4-Brain Core → Guard PolicyEvaluation 엔드포인트

흐름:
    POST /api/v1/guard/evaluate
      → commandos_brain_router.route()   [WO-005 추가]
      → confidence_score 주입된 ActionSpec
      → policy_engine.evaluate()
      → PolicyEvaluation 반환
"""
from fastapi import APIRouter

from backend.core.commandos.action_spec import ActionSpec, RiskLevel
from backend.core.guard.policy_engine import PolicyEvaluation, evaluate

router = APIRouter(prefix="/api/v1/guard", tags=["guard"])


@router.post("/evaluate", response_model=PolicyEvaluation)
async def evaluate_action(spec: ActionSpec) -> PolicyEvaluation:
    """
    ActionSpec을 받아 4-Brain Core 판단 후 Guard Policy 판정을 반환합니다.
    결과: allow / deny / ask

    [의존성] 연결: commandos_brain_router.route() / WO-005
    brain_router 실패 시 원본 spec으로 Guard 진행 (fallback 보장).
    """
    # WO-005: Brain Router — Guard 전 confidence_score 주입
    try:
        from backend.core.brain.commandos_brain_router import route as brain_route
        brain_result = await brain_route(spec)
        enriched_spec = brain_result.enriched_spec
    except Exception:
        # C-08 Fix: Brain 실패 시 공격자 제공 spec 기본값(risk=none) 사용 금지
        # → 고위험 + 승인 필수로 강제하여 allow 경로 차단
        enriched_spec = spec.model_copy(update={
            "risk_level": RiskLevel.high.value,
            "requires_approval": True,
        })

    return evaluate(enriched_spec)
