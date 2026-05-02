"""
HUD Bridge — WO-003
FastAPI 라우터: Extension HUD ↔ Web App 사이 ActionSpec 발급/조회/실행 엔드포인트

흐름:
  Extension HUD → POST /api/v1/action-spec/create → action_id 반환
  Web App       → GET  /api/v1/action-spec/{action_id} → 풀 ActionSpec 반환
  Web App       → POST /api/v1/action-spec/{action_id}/execute → 실행(stub)
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from backend.core.commandos.action_spec import (
    ActionSpec,
    ActionSpecCreateRequest,
    ActionSpecResponse,
    ExecutionState,
    make_preview_url,
)
from backend.core.commandos.ai_intent_bridge import parse_intent
from backend.core.commandos.action_preview import build_preview
from backend.core.guard.policy_engine import PolicyResult, evaluate

router = APIRouter(prefix="/api/v1/action-spec", tags=["action-spec"])

# 인메모리 저장소 — Phase 1 범위 (SQLite는 WO-010)
_store: dict[str, ActionSpec] = {}


@router.post("/create", response_model=ActionSpecResponse)
async def create_action_spec(req: ActionSpecCreateRequest) -> ActionSpecResponse:
    """
    자연어 입력 → ActionSpec 생성 → Guard 판정 → action_id 반환.
    Extension HUD에서 호출합니다.
    """
    spec = await parse_intent(raw_input=req.raw_input, source=req.source)
    guard_eval = evaluate(spec)
    spec.guard_result = guard_eval.result.value
    spec.guard_reason = guard_eval.reason

    if guard_eval.result == PolicyResult.ask or guard_eval.result == PolicyResult.deny:
        spec.requires_approval = True

    _store[spec.action_id] = spec

    preview_url: Optional[str] = None
    if spec.requires_approval or spec.risk_level != "none":
        preview_url = make_preview_url(spec.action_id)

    return ActionSpecResponse(
        action_id=spec.action_id,
        intent=spec.intent,
        target_type=spec.target_type,
        risk_level=spec.risk_level,
        requires_approval=spec.requires_approval,
        guard_result=spec.guard_result,
        guard_reason=spec.guard_reason,
        execution_state=spec.execution_state,
        confidence_score=spec.confidence_score,
        preview_url=preview_url,
    )


@router.get("/{action_id}", response_model=dict)
async def get_action_spec(action_id: str) -> dict:
    """
    action_id로 ActionSpec 풀 디테일 조회.
    Web App ActionPreviewPanel에서 호출합니다.
    """
    spec = _store.get(action_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"ActionSpec not found: {action_id}")

    preview = build_preview(spec)
    return {
        "spec": spec.model_dump(),
        "preview": preview,
    }


@router.post("/{action_id}/execute")
async def execute_action(action_id: str) -> dict:
    """
    사용자 승인 후 ActionSpec 실행.
    guard_result=deny인 경우 실행 거부.
    Phase 1 범위: 실행 로그만 기록 (실제 Execution Kernel은 WO-011+)
    """
    spec = _store.get(action_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"ActionSpec not found: {action_id}")

    if spec.guard_result == PolicyResult.deny.value:
        raise HTTPException(status_code=403, detail="Guard denied this action")

    spec.execution_state = ExecutionState.user_approved.value
    _store[action_id] = spec

    return {
        "action_id": action_id,
        "execution_state": spec.execution_state,
        "message": "Action approved. Execution kernel not yet connected (WO-011+).",
    }


@router.post("/{action_id}/reject")
async def reject_action(action_id: str) -> dict:
    """사용자가 Action Preview에서 취소."""
    spec = _store.get(action_id)
    if spec is None:
        raise HTTPException(status_code=404, detail=f"ActionSpec not found: {action_id}")

    spec.execution_state = ExecutionState.user_rejected.value
    _store[action_id] = spec

    return {
        "action_id": action_id,
        "execution_state": spec.execution_state,
    }
