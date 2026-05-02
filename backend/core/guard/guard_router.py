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

from backend.core.commandos.action_spec import ActionSpec
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
        # Brain Router 실패해도 Guard는 반드시 정상 진행
        enriched_spec = spec

    return evaluate(enriched_spec)
