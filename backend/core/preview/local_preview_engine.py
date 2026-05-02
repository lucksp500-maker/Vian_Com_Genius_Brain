"""
LocalPreviewEngine — WO-004
검색된 파일(PDF, 텍스트, 코드, 웹)의 실행 전 미리보기 데이터를 생성합니다.
실행 없이 내용을 보여주는 것이 목적 — 파일을 열거나 수정하지 않습니다.

흐름:
    preview_file(path) → PreviewResult → DocumentPreviewRoom.tsx
"""
from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from backend.core.indexer.document_metadata import mask_sensitive

_PREVIEW_MAX_CHARS = 2000   # 미리보기 최대 글자수
_PDF_MAX_PAGES = 5          # PDF 미리보기 최대 페이지 수


@dataclass
class PreviewResult:
    """
    단일 파일 미리보기 결과.

    흐름:
        preview_file(path) → PreviewResult → JSON 직렬화 → Frontend
    """
    path: str
    title: str
    file_type: str              # pdf / text / code / web / unknown
    content_preview: str        # 미리보기 텍스트 (최대 _PREVIEW_MAX_CHARS)
    page_count: Optional[int]   # PDF인 경우 총 페이지 수
    file_size: int              # bytes
    sensitive_flags: list[str] = field(default_factory=list)
    error: Optional[str] = None
    available: bool = True       # False이면 content_preview 없음

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "title": self.title,
            "file_type": self.file_type,
            "content_preview": self.content_preview,
            "page_count": self.page_count,
            "file_size": self.file_size,
            "sensitive_flags": self.sensitive_flags,
            "error": self.error,
            "available": self.available,
        }


def _preview_pdf_sync(file_path: str) -> PreviewResult:
    """PDF 파일에서 첫 몇 페이지 텍스트를 추출합니다. 동기 함수."""
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    title = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    try:
        reader = PdfReader(file_path)
        page_count = len(reader.pages)
        text_parts: list[str] = []

        for i, page in enumerate(reader.pages[:_PDF_MAX_PAGES]):
            try:
                text = page.extract_text() or ""
                text_parts.append(text)
            except Exception:
                continue  # 개별 페이지 실패 시 건너뜀

        raw_text = "\n".join(text_parts).strip()
        if not raw_text:
            raw_text = "(텍스트를 추출할 수 없는 PDF입니다. 이미지 기반이거나 암호화되었을 수 있습니다.)"

        masked_text, sensitive_flags = mask_sensitive(raw_text[:_PREVIEW_MAX_CHARS])

        return PreviewResult(
            path=file_path,
            title=title,
            file_type="pdf",
            content_preview=masked_text,
            page_count=page_count,
            file_size=file_size,
            sensitive_flags=sensitive_flags,
        )

    except PdfReadError as e:
        return PreviewResult(
            path=file_path,
            title=title,
            file_type="pdf",
            content_preview="",
            page_count=None,
            file_size=file_size,
            error=f"PDF 읽기 실패: {e}",
            available=False,
        )
    except Exception as e:
        return PreviewResult(
            path=file_path,
            title=title,
            file_type="pdf",
            content_preview="",
            page_count=None,
            file_size=file_size,
            error=f"예외 발생: {type(e).__name__}: {e}",
            available=False,
        )


def _preview_text_sync(file_path: str, file_type: str) -> PreviewResult:
    """텍스트/코드/웹 파일 미리보기. 동기 함수."""
    title = os.path.basename(file_path)
    file_size = os.path.getsize(file_path)

    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read(_PREVIEW_MAX_CHARS * 2)  # 마스킹 전 여유 있게 읽기

        masked_text, sensitive_flags = mask_sensitive(raw_text[:_PREVIEW_MAX_CHARS])

        return PreviewResult(
            path=file_path,
            title=title,
            file_type=file_type,
            content_preview=masked_text,
            page_count=None,
            file_size=file_size,
            sensitive_flags=sensitive_flags,
        )
    except PermissionError:
        return PreviewResult(
            path=file_path,
            title=title,
            file_type=file_type,
            content_preview="",
            page_count=None,
            file_size=file_size,
            error="읽기 권한이 없습니다.",
            available=False,
        )
    except Exception as e:
        return PreviewResult(
            path=file_path,
            title=title,
            file_type=file_type,
            content_preview="",
            page_count=None,
            file_size=file_size,
            error=f"예외 발생: {type(e).__name__}: {e}",
            available=False,
        )


def _preview_sync(file_path: str) -> PreviewResult:
    """파일 타입 감지 후 적합한 미리보기 함수 호출. 동기 함수."""
    if not os.path.exists(file_path):
        return PreviewResult(
            path=file_path,
            title=os.path.basename(file_path),
            file_type="unknown",
            content_preview="",
            page_count=None,
            file_size=0,
            error="파일을 찾을 수 없습니다.",
            available=False,
        )

    ext = Path(file_path).suffix.lower()

    if ext == ".pdf":
        return _preview_pdf_sync(file_path)

    if ext in {".txt", ".md", ".csv", ".json", ".yaml", ".yml"}:
        return _preview_text_sync(file_path, "text")

    if ext in {".py", ".js", ".ts", ".tsx", ".jsx"}:
        return _preview_text_sync(file_path, "code")

    if ext in {".html", ".htm"}:
        return _preview_text_sync(file_path, "web")

    # 지원하지 않는 파일 형식
    return PreviewResult(
        path=file_path,
        title=os.path.basename(file_path),
        file_type="unknown",
        content_preview="",
        page_count=None,
        file_size=os.path.getsize(file_path),
        error="미리보기를 지원하지 않는 파일 형식입니다.",
        available=False,
    )


class LocalPreviewEngine:
    """
    로컬 파일 미리보기 엔진.

    사용:
        engine = LocalPreviewEngine()
        result = await engine.preview_file("/path/to/doc.pdf")
    """

    async def preview_file(self, file_path: str) -> PreviewResult:
        """
        파일 미리보기 데이터를 생성합니다.
        asyncio.to_thread()로 이벤트 루프를 블록하지 않습니다.
        """
        return await asyncio.to_thread(_preview_sync, file_path)
