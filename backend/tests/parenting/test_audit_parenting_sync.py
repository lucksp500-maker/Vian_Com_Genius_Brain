"""
test_audit_parenting_sync.py — WO-006 테스트
AuditLedger + EventLogger + AuditToParentingSync 커버리지.

주요 검증:
1. 명령 1건 실행 → audit DB + parenting jsonl 동시 생성
2. audit_to_parenting_sync: 누락 이벤트 재동기화
3. EventLogger.read_recent() 정상 반환
4. execution_result=None 시 null safe 처리
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.core.audit.audit_ledger import AuditLedger, AuditRecord
from backend.core.parenting.event_logger import EventLogger, build_parenting_event
from backend.core.parenting.audit_to_parenting_sync import AuditToParentingSync


# ─── EventLogger ─────────────────────────────────────────────────

class TestEventLogger:
    @pytest.mark.asyncio
    async def test_log_event_creates_jsonl(self, tmp_path):
        """이벤트 기록 시 jsonl 파일 생성."""
        events_path = tmp_path / "parenting_events.jsonl"
        logger = EventLogger(events_path=events_path)
        event = build_parenting_event(
            raw_input="파일 검색",
            action_spec_id="spec-001",
            intent_class="파일 검색",
            risk_class="none",
            guard_result="allow",
            approval_state="pending",
            execution_state="executed",
        )
        await logger.log_event(event)
        assert events_path.exists()
        lines = [l.strip() for l in events_path.read_text(encoding="utf-8").split("\n") if l.strip()]
        assert len(lines) == 1
        data = json.loads(lines[0])
        assert data["intent_class"] == "파일 검색"
        assert data["feedback_class"] == "positive"

    @pytest.mark.asyncio
    async def test_multiple_events_appended(self, tmp_path):
        """여러 이벤트가 순서대로 append됨."""
        events_path = tmp_path / "parenting_events.jsonl"
        logger = EventLogger(events_path=events_path)
        for i in range(3):
            event = build_parenting_event(
                raw_input=f"명령 {i}",
                action_spec_id=f"spec-{i:03}",
                intent_class="파일 검색",
                risk_class="none",
                guard_result="allow",
                approval_state="approved",
                execution_state="executed",
            )
            await logger.log_event(event)
        recent = await logger.read_recent(limit=10)
        assert len(recent) == 3

    @pytest.mark.asyncio
    async def test_read_recent_from_empty_file(self, tmp_path):
        """빈 parenting 파일에서 read_recent → 빈 리스트."""
        events_path = tmp_path / "parenting_events.jsonl"
        logger = EventLogger(events_path=events_path)
        result = await logger.read_recent()
        assert result == []

    def test_build_parenting_event_schema(self):
        """build_parenting_event() 출력에 필수 필드 포함."""
        event = build_parenting_event(
            raw_input="테스트",
            action_spec_id="spec-test",
            intent_class="테스트 의도",
            risk_class="low",
            guard_result="ask",
            approval_state="approved",
            execution_state="executed",
            confidence=0.85,
        )
        for key in ("event_id", "timestamp", "raw_input", "action_spec_id",
                    "intent_class", "risk_class", "guard_result",
                    "execution_state", "feedback_class"):
            assert key in event
        assert event["confidence"] == 0.85

    def test_feedback_class_positive_on_executed(self):
        event = build_parenting_event(
            raw_input="x", action_spec_id="y",
            intent_class="z", risk_class="none",
            guard_result="allow", approval_state="approved",
            execution_state="executed",
        )
        assert event["feedback_class"] == "positive"

    def test_feedback_class_negative_on_failed(self):
        event = build_parenting_event(
            raw_input="x", action_spec_id="y",
            intent_class="z", risk_class="none",
            guard_result="allow", approval_state="approved",
            execution_state="failed",
        )
        assert event["feedback_class"] == "negative"

    def test_feedback_class_rejected_on_user_rejection(self):
        event = build_parenting_event(
            raw_input="x", action_spec_id="y",
            intent_class="z", risk_class="high",
            guard_result="ask", approval_state="user_rejected",
            execution_state="user_rejected",
        )
        assert event["feedback_class"] == "rejected"


# ─── AuditLedger ─────────────────────────────────────────────────

class TestAuditLedger:
    @pytest.mark.asyncio
    async def test_record_creates_audit_and_parenting(self, tmp_path):
        """명령 1건 → audit DB + parenting jsonl 동시 생성 (WO-006 핵심 완료 조건)."""
        db_path = tmp_path / "audit_ledger.sqlite"
        events_path = tmp_path / "parenting_events.jsonl"
        logger = EventLogger(events_path=events_path)
        ledger = AuditLedger(db_path=db_path, event_logger=logger)

        rec = AuditRecord(
            command="이 PDF 요약해줘",
            action_spec_id="spec-001",
            intent_class="문서 요약",
            risk_class="none",
            guard_decision="allow",
            approval_result="approved",
            execution_result="executed",
            raw_input="이 PDF 요약해줘",
            confidence=0.9,
        )
        audit_id = await ledger.record(rec)

        # audit DB 확인
        assert audit_id
        records = await ledger.list_recent(limit=5)
        assert len(records) == 1
        assert records[0]["command"] == "이 PDF 요약해줘"
        assert records[0]["intent_class"] == "문서 요약"

        # parenting jsonl 확인
        assert events_path.exists()
        lines = [l for l in events_path.read_text(encoding="utf-8").split("\n") if l.strip()]
        assert len(lines) == 1
        event = json.loads(lines[0])
        assert event["intent_class"] == "문서 요약"
        assert event["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_record_with_null_execution_result(self, tmp_path):
        """execution_result=None → null safe 처리."""
        db_path = tmp_path / "audit_ledger.sqlite"
        events_path = tmp_path / "parenting_events.jsonl"
        logger = EventLogger(events_path=events_path)
        ledger = AuditLedger(db_path=db_path, event_logger=logger)

        rec = AuditRecord(
            command="파일 이동",
            action_spec_id="spec-002",
            intent_class="파일 이동",
            risk_class="low",
            guard_decision="allow",
            approval_result="approved",
            execution_result=None,  # null
        )
        audit_id = await ledger.record(rec)
        assert audit_id
        records = await ledger.list_recent()
        assert records[0]["execution_result"] is None

    @pytest.mark.asyncio
    async def test_list_recent_returns_sorted(self, tmp_path):
        """list_recent는 최신 순으로 반환."""
        db_path = tmp_path / "audit_ledger.sqlite"
        events_path = tmp_path / "parenting_events.jsonl"
        ledger = AuditLedger(
            db_path=db_path,
            event_logger=EventLogger(events_path=events_path),
        )
        for i in range(3):
            await ledger.record(AuditRecord(
                command=f"명령 {i}",
                action_spec_id=f"spec-{i}",
                intent_class="테스트", risk_class="none",
            ))
        records = await ledger.list_recent(limit=3)
        # 최신이 첫 번째 (DESC 정렬)
        assert records[0]["command"] == "명령 2"


# ─── AuditToParentingSync ─────────────────────────────────────────

class TestAuditToParentingSync:
    @pytest.mark.asyncio
    async def test_sync_empty_audit_returns_zero(self, tmp_path):
        """audit DB 없을 때 sync → 0 반환."""
        sync = AuditToParentingSync(
            db_path=tmp_path / "audit.sqlite",
            events_path=tmp_path / "events.jsonl",
        )
        count = await sync.sync_missing()
        assert count == 0

    @pytest.mark.asyncio
    async def test_sync_missing_events(self, tmp_path):
        """audit DB에 있고 parenting에 없는 기록 → sync 후 jsonl에 추가됨."""
        db_path = tmp_path / "audit_ledger.sqlite"
        events_path = tmp_path / "parenting_events.jsonl"

        # audit DB에 1건 직접 생성 (event_logger 없이)
        logger = EventLogger(events_path=tmp_path / "dummy.jsonl")  # 별도 파일
        ledger = AuditLedger(db_path=db_path, event_logger=logger)
        await ledger.record(AuditRecord(
            command="테스트 명령",
            action_spec_id="spec-missing-001",
            intent_class="테스트", risk_class="none",
        ))

        # parenting는 비어있음 (sync가 채워야 함)
        sync = AuditToParentingSync(db_path=db_path, events_path=events_path)
        count = await sync.sync_missing()
        assert count == 1
        assert events_path.exists()
        lines = [l for l in events_path.read_text().split("\n") if l.strip()]
        assert len(lines) == 1

    @pytest.mark.asyncio
    async def test_sync_idempotent(self, tmp_path):
        """두 번 sync해도 중복 없음."""
        db_path = tmp_path / "audit_ledger.sqlite"
        events_path = tmp_path / "parenting_events.jsonl"
        logger = EventLogger(events_path=tmp_path / "dummy.jsonl")
        ledger = AuditLedger(db_path=db_path, event_logger=logger)
        await ledger.record(AuditRecord(
            command="테스트",
            action_spec_id="spec-idem-001",
            intent_class="테스트", risk_class="none",
        ))

        sync = AuditToParentingSync(db_path=db_path, events_path=events_path)
        c1 = await sync.sync_missing()
        c2 = await sync.sync_missing()
        assert c1 == 1
        assert c2 == 0  # 이미 sync됨
