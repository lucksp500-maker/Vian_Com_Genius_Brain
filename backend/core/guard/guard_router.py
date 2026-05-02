"""
Guard Router — WO-002
FastAPI 라우터: ActionSpec → Guard PolicyEvaluation 엔드포인트
"""
from fastapi import APIRouter

from backend.core.commandos.action_spec import ActionSpec
from backend.core.guard.policy_engine import PolicyEvaluation, evaluate

router = APIRouter(prefix="/api/v1/guard", tags=["guard"])


@router.post("/evaluate", response_model=PolicyEvaluation)
async def evaluate_action(spec: ActionSpec) -> PolicyEvaluation:
    """
    ActionSpec을 받아 Guard Policy 판정을 반환합니다.
    결과: allow / deny / ask
    """
    return evaluate(spec)
