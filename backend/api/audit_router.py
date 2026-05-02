"""
audit_router.py — WO-006
FastAPI 라우터: Audit Ledger + Undo Journal API 엔드포인트.
"""
from __future__ import annotations

import os

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from backend.core.audit.audit_ledger import AuditLedger
from backend.core.undo.undo_journal import UndoJournal

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])
undo_router = APIRouter(prefix="/api/v1/undo", tags=["undo"])

_ledger = AuditLedger()
_journal = UndoJournal()

# H-11 Fix: 내부 전용 엔드포인트 토큰 검증
# 환경변수 VIAN_INTERNAL_TOKEN 미설정 시 개발용 기본값 사용
_INTERNAL_TOKEN = os.environ.get("VIAN_INTERNAL_TOKEN", "vian-internal-v1")


def _verify_internal_token(x_internal_token: str = Header(...)) -> None:
    """POST 쓰기 엔드포인트 내부 전용 토큰 검증. 외부 요청 차단."""
    if x_internal_token != _INTERNAL_TOKEN:
        raise HTTPException(status_code=403, detail="내부 전용 엔드포인트입니다.")


# H-11 Fix: POST /api/v1/audit/record 엔드포인트 제거
# 이유: 인증 없는 공개 API로 누구나 audit 기록 삽입/위변조 가능
# 내부 AuditLedger.record()는 hud_bridge에서 직접 호출 — 외부 HTTP 노출 불필요
# (AuditRecordRequest, AuditRecordResponse 클래스도 함께 제거)


class AuditRecentResponse(BaseModel):
    records: list[dict]
    count: int


@router.get("/recent", response_model=AuditRecentResponse)
async def get_recent_audit(
    limit: int = Query(default=20, ge=1, le=100)
) -> AuditRecentResponse:
    """최근 Audit 기록을 반환합니다."""
    records = await _ledger.list_recent(limit=limit)
    return AuditRecentResponse(records=records, count=len(records))


class UndoRecordRequest(BaseModel):
    operation_type: str
    before_state: dict
    after_state: Optional[dict] = None
    action_id: str = ""


class UndoRecordResponse(BaseModel):
    undo_id: str
    undo_available: bool
    undo_method: str


class UndoRecentResponse(BaseModel):
    entries: list[dict]
    count: int


@undo_router.post("/record", response_model=UndoRecordResponse)
async def record_undo(req: UndoRecordRequest, _: None = Depends(_verify_internal_token)) -> UndoRecordResponse:
    """파일 작업 전/후 상태를 Undo Journal에 기록합니다."""
    undo_id = await _journal.record_operation(
        req.operation_type, req.before_state, req.after_state, req.action_id
    )
    entry = await _journal.get_entry(undo_id)
    return UndoRecordResponse(
        undo_id=undo_id,
        undo_available=entry.undo_available if entry else False,
        undo_method=entry.undo_method if entry else "",
    )


@undo_router.get("/recent", response_model=UndoRecentResponse)
async def get_recent_undo(
    limit: int = Query(default=20, ge=1, le=100)
) -> UndoRecentResponse:
    """최근 Undo Journal 기록을 반환합니다."""
    entries = await _journal.list_recent(limit=limit)
    return UndoRecentResponse(entries=entries, count=len(entries))
