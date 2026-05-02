"""
UndoJournal — WO-006
파일 이동/이름 변경/아카이브 저장 작업의 복구 정보를 undo_journal.sqlite에 기록합니다.

Phase 2 범위: 기록 전용 (undo 실행은 Phase 3).
undo_available=True이면 복구 가능한 작업임을 표시합니다.

흐름:
    파일 이동/이름변경 시작 전 → record_before()
    작업 완료 후 → record_after()
    또는 단일 호출 → record_operation() (before+after 모두 알 때)
"""
from __future__ import annotations

import asyncio
import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# [보호] 이유: undo_journal.sqlite 파일 위치 — 절대 이동 금지
# 수정 필요 시: main.py 환경변수로 경로 override 허용
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "undo_journal.sqlite"

# Phase 2에서 지원하는 undo 가능 작업 유형
_UNDOABLE_OPERATION_TYPES: set[str] = {
    "file_move",
    "file_rename",
    "archive_save",
    "browser_collection",
}

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS undo_journal (
    undo_id       TEXT PRIMARY KEY,
    action_id     TEXT NOT NULL DEFAULT '',
    operation_type TEXT NOT NULL,
    before_state  TEXT NOT NULL,   -- JSON
    after_state   TEXT,            -- JSON (작업 완료 후 채워짐)
    undo_available INTEGER NOT NULL DEFAULT 0,
    undo_method   TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL,
    completed_at  TEXT
);
CREATE INDEX IF NOT EXISTS idx_undo_action_id ON undo_journal(action_id);
CREATE INDEX IF NOT EXISTS idx_undo_created_at ON undo_journal(created_at DESC);
"""


def _init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        # H-09 Fix: WAL 모드 — 동시 읽기/쓰기 성능 개선 + 'database is locked' 방지
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(_CREATE_SQL)
        conn.commit()
    finally:
        conn.close()


@dataclass
class UndoEntry:
    """
    Undo Journal 단일 엔트리.

    설계도 섹션 H 기반 스키마:
        undo_id, action_id, before_state, after_state,
        undo_available, undo_method, created_at
    """
    undo_id: str
    action_id: str
    operation_type: str
    before_state: dict
    after_state: Optional[dict]
    undo_available: bool
    undo_method: str
    created_at: str
    completed_at: Optional[str] = None


def _describe_undo_method(operation_type: str, before_state: dict) -> str:
    """작업 유형 기반 undo 방법 텍스트 생성."""
    if operation_type == "file_move":
        return (
            f"파일을 '{before_state.get('dest_path', '?')}' 에서 "
            f"'{before_state.get('source_path', '?')}' 로 되돌립니다."
        )
    if operation_type == "file_rename":
        return (
            f"파일 이름을 '{before_state.get('new_name', '?')}' 에서 "
            f"'{before_state.get('original_name', '?')}' 로 되돌립니다."
        )
    if operation_type == "archive_save":
        return f"저장된 아카이브 '{before_state.get('archive_id', '?')}' 를 삭제합니다."
    return "이전 상태로 복구합니다."


def _insert_entry_sync(row: dict, db_path: Path) -> None:
    """undo_journal에 단일 엔트리 삽입. 동기 함수."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            """
            INSERT INTO undo_journal
                (undo_id, action_id, operation_type, before_state, after_state,
                 undo_available, undo_method, created_at, completed_at)
            VALUES
                (:undo_id, :action_id, :operation_type, :before_state, :after_state,
                 :undo_available, :undo_method, :created_at, :completed_at)
            """,
            row,
        )
        conn.commit()
    finally:
        conn.close()


def _update_after_state_sync(undo_id: str, after_state: dict, completed_at: str, db_path: Path) -> None:
    """after_state 업데이트. 동기 함수."""
    conn = sqlite3.connect(str(db_path))
    try:
        conn.execute(
            "UPDATE undo_journal SET after_state=?, undo_available=1, completed_at=? WHERE undo_id=?",
            (json.dumps(after_state, ensure_ascii=False), completed_at, undo_id),
        )
        conn.commit()
    finally:
        conn.close()


def _list_recent_sync(limit: int, db_path: Path) -> list[dict]:
    """최근 undo 기록 조회. 동기 함수."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM undo_journal ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()]
    finally:
        conn.close()


def _get_entry_sync(undo_id: str, db_path: Path) -> Optional[dict]:
    """undo_id로 단일 엔트리 조회. 동기 함수."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            "SELECT * FROM undo_journal WHERE undo_id=?", (undo_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


class UndoJournal:
    """
    Undo Journal — 파일 작업 전후 상태 기록.

    사용:
        journal = UndoJournal()
        undo_id = await journal.record_operation("file_move", before, after)
        entry = await journal.get_entry(undo_id)
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or _DB_PATH
        _init_db(self._db_path)

    async def record_operation(
        self,
        operation_type: str,
        before_state: dict,
        after_state: Optional[dict] = None,
        action_id: str = "",
    ) -> str:
        """
        작업 전/후 상태를 기록합니다.
        after_state가 None이면 undo_available=False (작업 미완료).
        반환값: undo_id
        """
        undo_id = str(uuid.uuid4())
        created_at = datetime.now(timezone.utc).isoformat()
        undo_available = after_state is not None and operation_type in _UNDOABLE_OPERATION_TYPES
        undo_method = _describe_undo_method(operation_type, before_state) if undo_available else ""

        row = {
            "undo_id": undo_id,
            "action_id": action_id,
            "operation_type": operation_type,
            "before_state": json.dumps(before_state, ensure_ascii=False),
            "after_state": json.dumps(after_state, ensure_ascii=False) if after_state else None,
            "undo_available": 1 if undo_available else 0,
            "undo_method": undo_method,
            "created_at": created_at,
            "completed_at": created_at if after_state else None,
        }
        await asyncio.to_thread(_insert_entry_sync, row, self._db_path)
        return undo_id

    async def complete_operation(self, undo_id: str, after_state: dict) -> None:
        """
        after_state를 업데이트하고 undo_available=True로 설정합니다.
        record_operation() 후 작업 완료 시 호출합니다.
        """
        completed_at = datetime.now(timezone.utc).isoformat()
        await asyncio.to_thread(
            _update_after_state_sync, undo_id, after_state, completed_at, self._db_path
        )

    async def get_entry(self, undo_id: str) -> Optional[UndoEntry]:
        """undo_id로 단일 엔트리를 조회합니다."""
        row = await asyncio.to_thread(_get_entry_sync, undo_id, self._db_path)
        if row is None:
            return None
        return UndoEntry(
            undo_id=row["undo_id"],
            action_id=row["action_id"],
            operation_type=row["operation_type"],
            before_state=json.loads(row["before_state"]),
            after_state=json.loads(row["after_state"]) if row["after_state"] else None,
            undo_available=bool(row["undo_available"]),
            undo_method=row["undo_method"],
            created_at=row["created_at"],
            completed_at=row["completed_at"],
        )

    async def list_recent(self, limit: int = 20) -> list[dict]:
        """최근 undo 기록을 반환합니다."""
        return await asyncio.to_thread(_list_recent_sync, limit, self._db_path)
