"""
BrowserRouter — WO-007
브라우저 자동화 어댑터 FastAPI 라우터.

엔드포인트:
    POST /api/v1/browser/dispatch   — Guard 승인 ActionSpec → 명령 큐 등록
    GET  /api/v1/browser/queue/next — Extension 폴링: 다음 명령 가져가기
    POST /api/v1/browser/result     — Extension DOM 추출 결과 수신
    POST /api/v1/browser/collect    — Extension 팝업 직접 푸시 (Guard 없이)
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional

from backend.core.browser.browser_automation_adapter import (
    BrowserAutomationAdapter,
    BrowserPushPayload,
    BrowserResult,
    _ALLOWED_EXEC_STATES,
)
from backend.core.commandos.action_spec import ActionSpec

router = APIRouter(prefix="/api/v1/browser", tags=["browser"])

# 싱글턴 어댑터 (앱 수명)
_adapter = BrowserAutomationAdapter()


# ─── 요청/응답 스키마 ─────────────────────────────────────────────

class DispatchRequest(BaseModel):
    """Guard 승인된 ActionSpec을 큐에 등록하는 요청."""
    action_spec: ActionSpec


class DispatchResponse(BaseModel):
    command_id: str
    queued: bool
    reason: str


class QueueNextResponse(BaseModel):
    command_id: str
    action_type: str
    action_spec_id: str


class ResultRequest(BaseModel):
    """Extension DOM 추출 결과 수신."""
    command_id: str
    action_type: str
    url: str
    title: str
    raw_content: str
    meta_description: str = ""
    word_count: int = 0


class ResultResponse(BaseModel):
    success: bool
    blocked: bool
    block_reason: str
    injection_risk: bool
    stored_content_length: int


class CollectRequest(BaseModel):
    """Extension 팝업 직접 푸시 (Guard 없이)."""
    action_type: str
    url: str
    title: str
    raw_content: str
    meta_description: str = ""
    word_count: int = 0


class CollectResponse(BaseModel):
    action_id: Optional[str]
    blocked: bool
    block_reason: str
    injection_risk: bool
    intent: Optional[str] = None
    risk_level: Optional[str] = None
    requires_approval: Optional[bool] = None
    preview_url: Optional[str] = None


# ─── 엔드포인트 ──────────────────────────────────────────────────

@router.post("/dispatch", response_model=DispatchResponse)
async def dispatch_command(req: DispatchRequest) -> DispatchResponse:
    """
    Guard 승인된 ActionSpec을 Extension 명령 큐에 등록합니다.
    Extension이 GET /queue/next 로 폴링하여 수거합니다.
    H-18 Fix: execution_state 사전 검증 — 미승인 spec 403 반환
    """
    # H-18 Fix: Guard/User 승인 없는 spec dispatch 차단 (HTTP 레이어 검증)
    # adapter.dispatch()도 동일 검증 수행하지만 API 레이어에서 명시적 403 반환
    if req.action_spec.execution_state not in _ALLOWED_EXEC_STATES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                f"dispatch 불가: execution_state='{req.action_spec.execution_state}' "
                f"(허용: {sorted(_ALLOWED_EXEC_STATES)})"
            ),
        )

    result = _adapter.dispatch(req.action_spec)
    return DispatchResponse(
        command_id=result.command_id,
        queued=result.queued,
        reason=result.reason,
    )


@router.get("/queue/next")
async def get_next_command() -> Response:
    """
    Extension 폴링 엔드포인트.
    대기 중인 명령이 있으면 200 + JSON 반환.
    큐가 비어있으면 204 No Content 반환.
    """
    cmd = _adapter.pop_next_command()
    if cmd is None:
        return Response(status_code=204)

    import json
    return Response(
        content=json.dumps({
            "command_id": cmd.command_id,
            "action_type": cmd.action_type,
            "action_spec_id": cmd.action_spec_id,
        }),
        status_code=200,
        media_type="application/json",
    )


@router.post("/result", response_model=ResultResponse)
async def receive_result(req: ResultRequest) -> ResultResponse:
    """
    Extension이 DOM 추출 후 전송하는 결과 수신.
    PromptInjectionShield 스캔 후 저장.
    """
    browser_result = BrowserResult(
        command_id=req.command_id,
        action_type=req.action_type,
        url=req.url,
        title=req.title,
        raw_content=req.raw_content,
        meta_description=req.meta_description,
        word_count=req.word_count,
    )
    result = _adapter.receive_result(browser_result)
    return ResultResponse(
        success=result.success,
        blocked=result.blocked,
        block_reason=result.block_reason,
        injection_risk=result.injection_risk,
        stored_content_length=result.stored_content_length,
    )


@router.post("/collect", response_model=CollectResponse)
async def collect_push(req: CollectRequest) -> CollectResponse:
    """
    Extension 팝업 직접 푸시 경로.
    ActionSpec 생성 + Guard 없이 Shield만 적용.
    """
    payload = BrowserPushPayload(
        action_type=req.action_type,
        url=req.url,
        title=req.title,
        raw_content=req.raw_content,
        meta_description=req.meta_description,
        word_count=req.word_count,
    )
    result = _adapter.receive_push(payload)

    if result.blocked:
        return CollectResponse(
            action_id=None,
            blocked=True,
            block_reason=result.block_reason,
            injection_risk=result.injection_risk,
        )

    spec = result.action_spec

    # H-06 Fix: collect 경로에 Guard 적용 — Shield만으로 보안 불충분
    # browser/collect는 Extension 팝업 직접 푸시 경로로 Guard를 우회함
    # evaluate()로 risk/target_type 기반 정책 검사 추가
    try:
        from backend.core.guard.policy_engine import PolicyResult, evaluate
        guard_result = evaluate(spec)
        if guard_result.result == PolicyResult.deny:
            return CollectResponse(
                action_id=None,
                blocked=True,
                block_reason=f"Guard 정책 거부: {guard_result.reason}",
                injection_risk=False,
            )
    except Exception:
        # Guard 실패 시 안전 측(차단) 처리 — C-08 원칙과 동일
        return CollectResponse(
            action_id=None,
            blocked=True,
            block_reason="Guard 평가 실패 — 안전을 위해 차단",
            injection_risk=False,
        )

    from backend.core.commandos.action_spec import make_preview_url
    # C-11 Fix: collect로 생성된 ActionSpec을 hud_bridge._store에 등록
    # 이전에는 _store에 없어서 preview_url → GET /action-spec/{id} → 404 발생
    from backend.core.commandos.hud_bridge import _store as _hud_store
    _hud_store[spec.action_id] = spec

    return CollectResponse(
        action_id=spec.action_id,
        blocked=False,
        block_reason="",
        injection_risk=False,
        intent=spec.intent,
        risk_level=spec.risk_level,
        requires_approval=spec.requires_approval,
        preview_url=make_preview_url(spec.action_id) if spec.requires_approval else None,
    )
