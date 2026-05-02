"""
audit_router.py — WO-006
FastAPI 라우터: Audit Ledger + Undo Journal API 엔드포인트.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import Optional

from backend.core.audit.audit_ledger import AuditLedger, AuditRecord
from backend.core.undo.undo_journal import UndoJournal

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])
undo_router = APIRouter(prefix="/api/v1/undo", tags=["undo"])

_ledger = AuditLedger()
_journal = UndoJournal()


class AuditRecordRequest(BaseModel):
    command: str
    action_spec_id: str = ""
    intent_class: str = ""
    risk_class: str = ""
    guard_decision: str = "pending"
    approval_result: str = "pending"
    execution_result: Optional[str] = None
    error: Optional[str] = None
    confidence: Optional[float] = None
    raw_input: str = ""


class AuditRecordResponse(BaseModel):
    audit_id: str


class AuditRecentResponse(BaseModel):
    records: list[dict]
    count: int


@router.post("/record", response_model=AuditRecordResponse)
async def record_audit(req: AuditRecordRequest) -> AuditRecordResponse:
    """명령 실행 이력을 Audit Ledger에 기록합니다."""
    rec = AuditRecord(
        command=req.command,
        action_spec_id=req.action_spec_id,
        intent_class=req.intent_class,
        risk_class=req.risk_class,
        guard_decision=req.guard_decision,
        approval_result=req.approval_result,
        execution_result=req.execution_result,
        error=req.error,
        confidence=req.confidence,
        raw_input=req.raw_input,
    )
    audit_id = await _ledger.record(rec)
    return AuditRecordResponse(audit_id=audit_id)


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
async def record_undo(req: UndoRecordRequest) -> UndoRecordResponse:
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
