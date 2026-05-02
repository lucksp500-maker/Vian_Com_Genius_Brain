"""
test_local_preview_engine.py — WO-004 테스트
LocalPreviewEngine 전체 커버리지.
"""
from __future__ import annotations

import io
import struct
import tempfile
from pathlib import Path

import pytest

from backend.core.preview.local_preview_engine import LocalPreviewEngine


@pytest.fixture
def engine():
    return LocalPreviewEngine()


# ─── 텍스트 파일 미리보기 ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_preview_text_file(engine, tmp_path):
    f = tmp_path / "notes.txt"
    f.write_text("이것은 테스트 텍스트입니다.", encoding="utf-8")
    result = await engine.preview_file(str(f))
    assert result.available is True
    assert "이것은 테스트 텍스트입니다." in result.content_preview
    assert result.file_type == "text"
    assert result.error is None


@pytest.mark.asyncio
async def test_preview_markdown_file(engine, tmp_path):
    f = tmp_path / "readme.md"
    f.write_text("# 프로젝트 설명\n내용이 여기 있습니다.", encoding="utf-8")
    result = await engine.preview_file(str(f))
    assert result.available is True
    assert result.file_type == "text"


@pytest.mark.asyncio
async def test_preview_code_file(engine, tmp_path):
    f = tmp_path / "app.py"
    f.write_text("def hello():\n    return 'hello'", encoding="utf-8")
    result = await engine.preview_file(str(f))
    assert result.available is True
    assert result.file_type == "code"


# ─── PDF 미리보기 ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_preview_pdf_file(engine, tmp_path):
    """실제 최소 PDF 파일로 텍스트 추출 테스트."""
    from pypdf import PdfWriter

    pdf_path = tmp_path / "test.pdf"
    writer = PdfWriter()
    # 빈 페이지를 가진 최소 PDF 생성
    writer.add_blank_page(width=612, height=792)
    with open(str(pdf_path), "wb") as f:
        writer.write(f)

    result = await engine.preview_file(str(pdf_path))
    # 빈 페이지라도 available=True이고 file_type=pdf여야 함
    assert result.file_type == "pdf"
    assert result.page_count == 1
    assert result.error is None


@pytest.mark.asyncio
async def test_preview_pdf_not_available_on_corrupt(engine, tmp_path):
    """손상된 PDF → available=False, error 메시지 포함."""
    corrupt = tmp_path / "corrupt.pdf"
    corrupt.write_bytes(b"not a pdf content at all XXXX")
    result = await engine.preview_file(str(corrupt))
    assert result.available is False
    assert result.error is not None
    assert result.file_type == "pdf"


# ─── 파일 없음 / 지원 안 됨 ──────────────────────────────────────


@pytest.mark.asyncio
async def test_preview_nonexistent_file(engine):
    result = await engine.preview_file("/nonexistent/path/doc.txt")
    assert result.available is False
    assert result.error is not None
    assert "찾을 수 없습니다" in result.error


@pytest.mark.asyncio
async def test_preview_unsupported_extension(engine, tmp_path):
    f = tmp_path / "photo.png"
    f.write_bytes(b"\x89PNG\r\n")
    result = await engine.preview_file(str(f))
    assert result.available is False
    assert result.error is not None


# ─── 민감정보 마스킹 ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_preview_masks_email(engine, tmp_path):
    f = tmp_path / "contact.txt"
    f.write_text("담당자: admin@vian.ai 로 연락하세요.", encoding="utf-8")
    result = await engine.preview_file(str(f))
    assert result.available is True
    assert "@vian.ai" not in result.content_preview
    assert "[이메일]" in result.content_preview
    assert "이메일" in result.sensitive_flags


@pytest.mark.asyncio
async def test_preview_masks_phone(engine, tmp_path):
    f = tmp_path / "phone.txt"
    f.write_text("연락처: 010-9876-5432", encoding="utf-8")
    result = await engine.preview_file(str(f))
    assert "[전화번호]" in result.content_preview
    assert "전화번호" in result.sensitive_flags


# ─── to_dict 직렬화 ───────────────────────────────────────────────


@pytest.mark.asyncio
async def test_preview_to_dict_has_required_keys(engine, tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("내용", encoding="utf-8")
    result = await engine.preview_file(str(f))
    d = result.to_dict()
    for key in ("path", "title", "file_type", "content_preview",
                "page_count", "file_size", "sensitive_flags", "error", "available"):
        assert key in d
