"""
DocumentMetadata — WO-004
로컬 파일/다운로드 항목의 메타데이터 추출 스키마.
LocalIndexer가 생성하고 local_index.sqlite에 저장합니다.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


# 민감정보 마스킹 패턴 — LocalPreviewEngine도 동일하게 사용
_SENSITIVE_PATTERNS: list[tuple[str, str]] = [
    (r"\b\d{6}[-\s]?\d{7}\b", "[주민번호]"),            # 주민등록번호 형식
    (r"\b\d{3}[-\s]\d{4}[-\s]\d{4}\b", "[전화번호]"),   # 전화번호 형식
    (r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", "[이메일]"),
    (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[카드번호]"),      # 카드번호 형식
]


def mask_sensitive(text: str) -> tuple[str, list[str]]:
    """
    텍스트에서 민감정보를 마스킹합니다.

    반환:
        (masked_text, detected_flags)
    """
    flags: list[str] = []
    result = text
    for pattern, replacement in _SENSITIVE_PATTERNS:
        if re.search(pattern, result):
            result = re.sub(pattern, replacement, result)
            flags.append(replacement.strip("[]"))
    return result, flags


# 색인 대상 확장자
INDEXABLE_EXTENSIONS: set[str] = {
    ".txt", ".md", ".pdf", ".docx", ".doc",
    ".html", ".htm", ".csv", ".json", ".yaml", ".yml",
    ".py", ".js", ".ts", ".tsx", ".jsx",
}


@dataclass
class DocumentMetadata:
    """
    로컬 파일 1건의 색인 메타데이터.

    흐름:
        os.walk → extract_metadata() → DocumentMetadata → SQLite
    """
    item_id: str = ""
    path: str = ""
    title: str = ""
    file_type: str = ""         # pdf / text / code / web / unknown
    last_modified: float = 0.0
    file_size: int = 0
    summary: str = ""           # 첫 200자 (텍스트만)
    sensitive_flags: list[str] = field(default_factory=list)
    indexed_at: float = 0.0

    @property
    def last_modified_dt(self) -> datetime:
        return datetime.fromtimestamp(self.last_modified, tz=timezone.utc)

    def to_dict(self) -> dict:
        return {
            "item_id": self.item_id,
            "path": self.path,
            "title": self.title,
            "file_type": self.file_type,
            "last_modified": self.last_modified,
            "file_size": self.file_size,
            "summary": self.summary,
            "sensitive_flags": ",".join(self.sensitive_flags),
            "indexed_at": self.indexed_at,
        }


def classify_file_type(path: str) -> str:
    """확장자 기반 파일 타입 분류."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".pdf":
        return "pdf"
    if ext in {".txt", ".md", ".csv", ".yaml", ".yml", ".json"}:
        return "text"
    if ext in {".py", ".js", ".ts", ".tsx", ".jsx"}:
        return "code"
    if ext in {".html", ".htm"}:
        return "web"
    return "unknown"


def extract_metadata(file_path: str, item_id: str) -> Optional[DocumentMetadata]:
    """
    파일 경로에서 DocumentMetadata를 추출합니다.
    색인 대상 확장자가 아니면 None 반환.
    권한 오류 발생 시 None 반환 (silent skip).
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in INDEXABLE_EXTENSIONS:
        return None

    try:
        stat = os.stat(file_path)
    except (PermissionError, FileNotFoundError, OSError):
        return None

    title = os.path.basename(file_path)
    file_type = classify_file_type(file_path)

    meta = DocumentMetadata(
        item_id=item_id,
        path=file_path,
        title=title,
        file_type=file_type,
        last_modified=stat.st_mtime,
        file_size=stat.st_size,
        indexed_at=datetime.now(timezone.utc).timestamp(),
    )
    return meta
