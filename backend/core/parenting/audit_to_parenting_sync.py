"""
AuditToParentingSync — WO-006
Audit Ledger → Parenting Events 동기화 유틸리티.

주 경로: AuditLedger.record()가 EventLogger를 직접 Push 호출 (실시간).
이 모듈: 보완 목적 — audit DB에는 있지만 parenting에 누락된 기록을 재동기화합니다.

사용 시나리오:
- 서버 재시작 후 누락된 이벤트 복구
- 테스트에서 audit DB ↔ parenting 동기 상태 검증
"""
from __future__ import annotations

import asyncio
import sqlite3
from pathlib import Path
from typing import Optional

from backend.core.parenting.event_logger import EventLogger, build_parenting_event

_DEFAULT_DB = Path(__file__).parent.parent.parent / "data" / "audit_ledger.sqlite"
_DEFAULT_EVENTS = Path(__file__).parent.parent.parent / "data" / "parenting_events.jsonl"


def _load_audit_ids_from_events_sync(events_path: Path) -> set[str]:
    """parenting_events.jsonl에서 이미 기록된 action_spec_id 집합 반환."""
    import json
    ids: set[str] = set()
    if not events_path.exists():
        return ids
    try:
        with open(str(events_path), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        ev = json.loads(line)
                        if ev.get("action_spec_id"):
                            ids.add(ev["action_spec_id"])
                    except Exception:
                        continue
    except OSError:
        pass
    return ids


def _load_audit_records_sync(db_path: Path) -> list[dict]:
    """audit_ledger.sqlite에서 모든 기록 반환."""
    if not db_path.exists():
        return []
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        return [dict(r) for r in conn.execute(
            "SELECT * FROM audit_ledger ORDER BY created_at ASC"
        ).fetchall()]
    except Exception:
        return []
    finally:
        conn.close()


class AuditToParentingSync:
    """
    Audit Ledger → Parenting Events 재동기화.

    사용:
        sync = AuditToParentingSync()
        synced_count = await sync.sync_missing()
    """

    def __init__(
        self,
        db_path: Optional[Path] = None,
        events_path: Optional[Path] = None,
    ):
        self._db_path = db_path or _DEFAULT_DB
        self._events_path = events_path or _DEFAULT_EVENTS
        self._logger = EventLogger(events_path=self._events_path)

    async def sync_missing(self) -> int:
        """
        audit_ledger에는 있지만 parenting_events에 없는 기록을 동기화합니다.
        반환값: 동기화된 이벤트 수.
        """
        # 1. 이미 parenting에 있는 action_spec_id 집합 확인
        existing_ids = await asyncio.to_thread(
            _load_audit_ids_from_events_sync, self._events_path
        )

        # 2. audit 전체 기록 로드
        audit_records = await asyncio.to_thread(
            _load_audit_records_sync, self._db_path
        )

        # 3. 누락된 것만 동기화
        synced = 0
        for rec in audit_records:
            action_spec_id = rec.get("action_spec_id", "")
            if action_spec_id and action_spec_id in existing_ids:
                continue

            event = build_parenting_event(
                raw_input=rec.get("command", ""),
                action_spec_id=action_spec_id,
                intent_class=rec.get("intent_class", ""),
                risk_class=rec.get("risk_class", ""),
                guard_result=rec.get("guard_decision"),
                approval_state=rec.get("approval_result", "pending"),
                execution_state=rec.get("execution_result") or "pending",
                confidence=rec.get("confidence"),
            )
            await self._logger.log_event(event)
            synced += 1

        return synced
