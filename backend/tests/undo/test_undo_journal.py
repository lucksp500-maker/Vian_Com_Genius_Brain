"""
test_undo_journal.py — WO-006 테스트
UndoJournal 전체 커버리지.

주요 검증:
1. 파일 이동 1건 → before_state/after_state/undo_method 저장
2. undo_available=False 경로 처리
3. 지원하지 않는 operation_type → undo_available=False
4. get_entry() 정확한 UndoEntry 반환
"""
from __future__ import annotations

from pathlib import Path

import pytest

from backend.core.undo.undo_journal import UndoJournal


@pytest.fixture
def journal(tmp_path):
    return UndoJournal(db_path=tmp_path / "undo_journal.sqlite")


# ─── 기본 기록 ────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_record_file_move_with_before_after(journal):
    """파일 이동 → before/after/undo_method 저장 (WO-006 핵심 완료 조건)."""
    before = {"source_path": "/home/user/Downloads/견적서.pdf", "dest_path": "/home/user/Documents/"}
    after = {"moved_to": "/home/user/Documents/견적서.pdf", "success": True}

    undo_id = await journal.record_operation("file_move", before, after, action_id="act-001")
    assert undo_id

    entry = await journal.get_entry(undo_id)
    assert entry is not None
    assert entry.operation_type == "file_move"
    assert entry.before_state == before
    assert entry.after_state == after
    assert entry.undo_available is True
    assert entry.undo_method != ""
    assert "Documents" in entry.undo_method or "Downloads" in entry.undo_method


@pytest.mark.asyncio
async def test_record_file_rename(journal):
    """파일 이름 변경 → undo 가능."""
    before = {"original_name": "견적서.pdf", "new_name": "최종견적서_2026.pdf"}
    after = {"renamed_to": "최종견적서_2026.pdf", "success": True}

    undo_id = await journal.record_operation("file_rename", before, after)
    entry = await journal.get_entry(undo_id)
    assert entry is not None
    assert entry.undo_available is True
    assert "최종견적서_2026.pdf" in entry.undo_method or "견적서.pdf" in entry.undo_method


@pytest.mark.asyncio
async def test_record_without_after_state_not_undoable(journal):
    """after_state=None → undo_available=False (작업 미완료)."""
    before = {"source_path": "/home/user/old.txt"}
    undo_id = await journal.record_operation("file_move", before, None)
    entry = await journal.get_entry(undo_id)
    assert entry is not None
    assert entry.undo_available is False
    assert entry.after_state is None


@pytest.mark.asyncio
async def test_complete_operation_sets_undo_available(journal):
    """record_before → complete_operation → undo_available=True."""
    before = {"source_path": "/home/user/file.txt", "dest_path": "/home/user/archive/"}
    undo_id = await journal.record_operation("file_move", before, None)

    after = {"moved_to": "/home/user/archive/file.txt", "success": True}
    await journal.complete_operation(undo_id, after)

    entry = await journal.get_entry(undo_id)
    assert entry is not None
    assert entry.undo_available is True
    assert entry.after_state == after
    assert entry.completed_at is not None


@pytest.mark.asyncio
async def test_unsupported_operation_not_undoable(journal):
    """지원하지 않는 operation_type → undo_available=False."""
    before = {"data": "some_data"}
    after = {"result": "done"}
    undo_id = await journal.record_operation("unknown_op", before, after)
    entry = await journal.get_entry(undo_id)
    assert entry is not None
    assert entry.undo_available is False


@pytest.mark.asyncio
async def test_get_nonexistent_entry_returns_none(journal):
    """존재하지 않는 undo_id → None."""
    result = await journal.get_entry("nonexistent-id-xyz")
    assert result is None


@pytest.mark.asyncio
async def test_list_recent_returns_sorted(journal):
    """list_recent는 최신 순으로 반환."""
    for i in range(3):
        await journal.record_operation(
            "file_move",
            {"source_path": f"/path/{i}.txt"},
            {"moved_to": f"/archive/{i}.txt"},
        )
    entries = await journal.list_recent(limit=5)
    assert len(entries) == 3
    # created_at 내림차순 (최신이 첫 번째)
    assert entries[0]["created_at"] >= entries[1]["created_at"]


@pytest.mark.asyncio
async def test_list_recent_empty(journal):
    """빈 journal → 빈 리스트."""
    result = await journal.list_recent()
    assert result == []


@pytest.mark.asyncio
async def test_archive_save_undoable(journal):
    """archive_save 작업 → undo 가능."""
    before = {"archive_id": "arc-001", "url": "https://example.com"}
    after = {"saved_to": "local_archive/arc-001.json"}
    undo_id = await journal.record_operation("archive_save", before, after)
    entry = await journal.get_entry(undo_id)
    assert entry.undo_available is True


@pytest.mark.asyncio
async def test_action_id_stored(journal):
    """action_id가 정확히 저장됨."""
    before = {"source_path": "/home/user/doc.pdf"}
    after = {"moved_to": "/home/user/archive/doc.pdf"}
    undo_id = await journal.record_operation("file_move", before, after, action_id="action-XYZ")
    entry = await journal.get_entry(undo_id)
    assert entry.action_id == "action-XYZ"
