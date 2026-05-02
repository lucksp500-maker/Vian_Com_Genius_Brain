"""
test_local_indexer.py — WO-004 테스트
LocalIndexer + DocumentMetadata 전체 커버리지.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from backend.core.indexer.document_metadata import (
    classify_file_type,
    extract_metadata,
    mask_sensitive,
)
from backend.core.indexer.local_indexer import LocalIndexer


# ─── document_metadata 단위 테스트 ────────────────────────────────


class TestMaskSensitive:
    def test_masks_email(self):
        text = "연락처: test@example.com 입니다"
        masked, flags = mask_sensitive(text)
        assert "[이메일]" in masked
        assert "이메일" in flags

    def test_masks_phone(self):
        text = "번호: 010-1234-5678 로 연락하세요"
        masked, flags = mask_sensitive(text)
        assert "[전화번호]" in masked
        assert "전화번호" in flags

    def test_no_sensitive_data(self):
        text = "이 문서는 일반 텍스트입니다."
        masked, flags = mask_sensitive(text)
        assert masked == text
        assert flags == []

    def test_multiple_patterns(self):
        text = "이메일 test@test.com 전화 010-0000-1111"
        masked, flags = mask_sensitive(text)
        assert len(flags) == 2


class TestClassifyFileType:
    def test_pdf(self):
        assert classify_file_type("report.pdf") == "pdf"

    def test_text(self):
        assert classify_file_type("notes.txt") == "text"
        assert classify_file_type("readme.md") == "text"
        assert classify_file_type("data.json") == "text"

    def test_code(self):
        assert classify_file_type("app.py") == "code"
        assert classify_file_type("index.ts") == "code"

    def test_web(self):
        assert classify_file_type("page.html") == "web"

    def test_unknown(self):
        assert classify_file_type("image.png") == "unknown"
        assert classify_file_type("video.mp4") == "unknown"


class TestExtractMetadata:
    def test_extracts_txt_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("hello world", encoding="utf-8")
        meta = extract_metadata(str(f), "id-001")
        assert meta is not None
        assert meta.title == "test.txt"
        assert meta.file_type == "text"
        assert meta.item_id == "id-001"
        assert meta.file_size > 0

    def test_skips_non_indexable(self, tmp_path):
        f = tmp_path / "image.png"
        f.write_bytes(b"\x89PNG")
        meta = extract_metadata(str(f), "id-002")
        assert meta is None

    def test_returns_none_for_missing_file(self):
        meta = extract_metadata("/nonexistent/path/file.txt", "id-003")
        assert meta is None

    def test_to_dict_has_required_keys(self, tmp_path):
        f = tmp_path / "doc.md"
        f.write_text("# 제목", encoding="utf-8")
        meta = extract_metadata(str(f), "id-004")
        assert meta is not None
        d = meta.to_dict()
        for key in ("item_id", "path", "title", "file_type", "last_modified",
                    "file_size", "summary", "sensitive_flags", "indexed_at"):
            assert key in d


# ─── LocalIndexer 통합 테스트 ─────────────────────────────────────


@pytest.fixture
def tmp_scan_dir(tmp_path):
    """테스트용 임시 다운로드 폴더 생성."""
    dl = tmp_path / "Downloads"
    dl.mkdir()
    (dl / "견적서_2026.txt").write_text("견적 금액: 1,200,000원", encoding="utf-8")
    (dl / "프레젠테이션.md").write_text("# 발표 자료\n내용", encoding="utf-8")
    (dl / "사진.png").write_bytes(b"\x89PNG\r\n")  # 색인 대상 아님
    return dl


@pytest.mark.asyncio
async def test_scan_and_index_returns_count(tmp_path, tmp_scan_dir):
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    count = await indexer.scan_and_index()
    assert count == 2  # txt + md, png 제외


@pytest.mark.asyncio
async def test_search_finds_indexed_file(tmp_path, tmp_scan_dir):
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    await indexer.scan_and_index()
    results = await indexer.search("견적서")
    assert len(results) == 1
    assert "견적서" in results[0]["title"]


@pytest.mark.asyncio
async def test_search_empty_query_returns_recent(tmp_path, tmp_scan_dir):
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    await indexer.scan_and_index()
    results = await indexer.search("")
    assert len(results) == 2


@pytest.mark.asyncio
async def test_search_no_results(tmp_path, tmp_scan_dir):
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    await indexer.scan_and_index()
    results = await indexer.search("존재하지않는파일명XYZXYZ")
    assert results == []


@pytest.mark.asyncio
async def test_scan_nonexistent_dir_returns_zero(tmp_path):
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=["/nonexistent/path/downloads"])
    count = await indexer.scan_and_index()
    assert count == 0


@pytest.mark.asyncio
async def test_scan_empty_dir_returns_zero(tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(empty_dir)])
    count = await indexer.scan_and_index()
    assert count == 0


@pytest.mark.asyncio
async def test_count_after_index(tmp_path, tmp_scan_dir):
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    await indexer.scan_and_index()
    total = await indexer.count()
    assert total == 2


@pytest.mark.asyncio
async def test_search_special_chars_dont_cause_error(tmp_path, tmp_scan_dir):
    """SQL 인젝션 위험 문자 입력 시 에러 없이 빈 결과 반환."""
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    await indexer.scan_and_index()
    results = await indexer.search("%'; DROP TABLE local_index; --")
    # 에러 없이 반환되면 성공
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_upsert_idempotent(tmp_path, tmp_scan_dir):
    """같은 디렉토리 두 번 스캔해도 중복 없음."""
    db = tmp_path / "test_index.sqlite"
    indexer = LocalIndexer(db_path=db, scan_dirs=[str(tmp_scan_dir)])
    await indexer.scan_and_index()
    await indexer.scan_and_index()
    total = await indexer.count()
    assert total == 2
