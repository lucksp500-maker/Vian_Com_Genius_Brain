"""
AuditLedger — WO-006
CommandOS 명령 실행 이력을 audit_ledger.sqlite에 기록합니다.
기록 즉시 event_logger.log_event()를 Push 호출하여 parenting_events.jsonl도 동시 생성합니다.

흐름:
    명령 실행 완료 → audit_ledger.record() → SQLite 저장
                                             → EventLogger.log_event() (Push)
                                             → parenting_events.jsonl 저장
"""
from __future__ import annotations

import asyncio
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.core.parenting.event_logger import EventLogger, build_parenting_event

# [의존성] 연결: event_logger.py (push target) / 단독 수정 금지
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "audit_ledger.sqlite"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS audit_ledger (
    audit_id          TEXT PRIMARY KEY,
    command           TEXT NOT NULL,
    action_spec_id    TEXT NOT NULL DEFAULT '',
    intent_class      TEXT NOT NULL DEFAULT '',
    risk_class        TEXT NOT NULL DEFAULT '',
    guard_decision    TEXT NOT NULL DEFAULT 'pending',
    approval_result   TEXT NOT NULL DEFAULT 'pending',
    execution_result  TEXT,
    error             TEXT,
    confidence        REAL,
    created_at        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_audit_created_at ON audit_ledger(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_intent ON audit_ledger(intent_class);
"""


def _init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_CREATE_SQL)
        conn.commit()
    finally:
        conn.close()


@dataclass
class AuditRecord:
    """
    Audit Ledger 단일 기록.

    설계도 섹션 H 기반 스키마:
        audit_id, command, action_spec_id, guard_decision,
        approval_result, execution_result, error, created_at
    """
    command: str
    action_spec_id: str = ""
    intent_class: str = ""
    risk_class: str = ""
    guard_decision: str = "pending"    # allow / deny / ask / pending
    approval_result: str = "pending"   # approved / rejected / pending
    execution_result: Optional[str] = None
    error: Optional[str] = None
    confidence: Optional[float] = None
    raw_input: str = ""

    def to_dict(self, audit_id: str, created_at: str) -> dict:
        return {
            "audit_id": audit_id,
            "command": self.command,
            "action_spec_id": self.action_spec_id,
            "intent_class": self.intent_class,
            "risk_class": self.risk_class,
            "guard_decision": self.guard_decision,
            "approval_result": self.approval_result,
            "execution_result": self.execution_result,
            "error": self.error,
            "confidence": self.confidence,
            "created_at": created_at,
        }


def _insert_audit_sync(record_dict: dict, db_path: Path) -> None:
    """audit_ledger SQLite에 단일 레코드 삽입. 동기 함수."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT INTO audit_ledger
                (audit_id, command, action_spec_id, intent_class, risk_class,
                 guard_decision, approval_result, execution_result, error,
                 confidence, created_at)
            VALUES
                (:audit_id, :command, :action_spec_id, :intent_class, :risk_class,
                 :guard_decision, :approval_result, :execution_result, :error,
                 :confidence, :created_at)
            """,
            record_dict,
        )
        conn.commit()
    finally:
        conn.close()


def _list_recent_sync(limit: int, db_path: Path) -> list[dict]:
    """최근 audit 기록 조회. 동기 함수."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM audit_ledger ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


class AuditLedger:
    """
    Audit Ledger — 명령 이력 저장 + Parenting Event 동시 생성.

    사용:
        ledger = AuditLedger()
        audit_id = await ledger.record(AuditRecord(...))
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        event_logger: Optional[EventLogger] = None,
    ):
        self._db_path = db_path or _DB_PATH
        self._event_logger = event_logger or EventLogger()
        _init_db(self._db_path)

    async def record(self, rec: AuditRecord) -> str:
        """
        Audit 기록을 SQLite에 저장하고 parenting_events.jsonl에 Push합니다.
        반환값: audit_id
        """
        audit_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        record_dict = rec.to_dict(audit_id, created_at)

        # 1. SQLite 저장
        await asyncio.to_thread(_insert_audit_sync, record_dict, self._db_path)

        # 2. Parenting Event Push (null safe)
        try:
            parenting_event = build_parenting_event(
                raw_input=rec.raw_input or rec.command,
                action_spec_id=rec.action_spec_id,
                intent_class=rec.intent_class,
                risk_class=rec.risk_class,
                guard_result=rec.guard_decision,
                approval_state=rec.approval_result,
                execution_state=rec.execution_result or "pending",
                confidence=rec.confidence,
            )
            await self._event_logger.log_event(parenting_event)
        except Exception:
            # Parenting 실패는 Audit 성공에 영향 없음
            pass

        return audit_id

    async def list_recent(self, limit: int = 20) -> list[dict]:
        """최근 audit 기록을 반환합니다."""
        return await asyncio.to_thread(_list_recent_sync, limit, self._db_path)
