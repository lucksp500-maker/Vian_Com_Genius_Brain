"""
LocalIndexer — WO-004
로컬 파일/다운로드 폴더를 SQLite(local_index.sqlite)로 색인합니다.
FastAPI 비동기 컨텍스트 안전: 모든 SQLite 호출은 asyncio.to_thread() 사용.

흐름:
    scan_directories() → DocumentMetadata 목록 → upsert_all() → SQLite
    search(query)       → SQLite LIKE 검색 → List[DocumentMetadata]
"""
from __future__ import annotations

import asyncio
import os
import sqlite3
import uuid
from pathlib import Path
from typing import Optional

from backend.core.indexer.document_metadata import (
    DocumentMetadata,
    extract_metadata,
)

# DB 경로 — backend/data/ 하위에 자동 생성
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "local_index.sqlite"

# 기본 스캔 대상 디렉토리 목록 (환경에 따라 교체 가능)
DEFAULT_SCAN_DIRS: list[str] = [
    str(Path.home() / "Downloads"),
    str(Path.home() / "Documents"),
    str(Path.home() / "Desktop"),
]

_MAX_FILES_PER_DIR = 2000  # 단일 디렉토리 최대 색인 파일 수 (안전 장치)


# ─── SQLite 스키마 ────────────────────────────────────────────────


_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS local_index (
    item_id       TEXT PRIMARY KEY,
    path          TEXT NOT NULL UNIQUE,
    title         TEXT NOT NULL,
    file_type     TEXT NOT NULL,
    last_modified REAL NOT NULL,
    file_size     INTEGER NOT NULL,
    summary       TEXT NOT NULL DEFAULT '',
    sensitive_flags TEXT NOT NULL DEFAULT '',
    indexed_at    REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_local_index_title ON local_index(title);
CREATE INDEX IF NOT EXISTS idx_local_index_last_modified ON local_index(last_modified DESC);
"""


def _init_db(db_path: Path) -> None:
    """DB 파일과 테이블을 초기화합니다 (없으면 생성)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript(_CREATE_SQL)
        conn.commit()
    finally:
        conn.close()


def _upsert_all_sync(records: list[DocumentMetadata], db_path: Path) -> int:
    """DocumentMetadata 목록을 SQLite에 upsert. 동기 함수 — to_thread로 호출."""
    if not records:
        return 0
    conn = sqlite3.connect(str(db_path))
    try:
        conn.executemany(
            """
            INSERT INTO local_index
                (item_id, path, title, file_type, last_modified, file_size,
                 summary, sensitive_flags, indexed_at)
            VALUES
                (:item_id, :path, :title, :file_type, :last_modified, :file_size,
                 :summary, :sensitive_flags, :indexed_at)
            ON CONFLICT(path) DO UPDATE SET
                title=excluded.title,
                file_type=excluded.file_type,
                last_modified=excluded.last_modified,
                file_size=excluded.file_size,
                summary=excluded.summary,
                sensitive_flags=excluded.sensitive_flags,
                indexed_at=excluded.indexed_at
            """,
            [r.to_dict() for r in records],
        )
        conn.commit()
        return len(records)
    finally:
        conn.close()


def _search_sync(query: str, limit: int, db_path: Path) -> list[dict]:
    """LIKE 검색. 동기 함수 — to_thread로 호출."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    try:
        if not query.strip():
            # 빈 쿼리 → 최근 항목 반환
            rows = conn.execute(
                "SELECT * FROM local_index ORDER BY last_modified DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            # 특수문자 에스케이프 후 LIKE 검색
            escaped = query.replace("%", "\\%").replace("_", "\\_")
            pattern = f"%{escaped}%"
            rows = conn.execute(
                """
                SELECT * FROM local_index
                WHERE title LIKE ? ESCAPE '\\'
                   OR summary LIKE ? ESCAPE '\\'
                ORDER BY last_modified DESC
                LIMIT ?
                """,
                (pattern, pattern, limit),
            ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def _scan_directory_sync(directory: str) -> list[DocumentMetadata]:
    """
    단일 디렉토리를 재귀 스캔하여 DocumentMetadata 목록 반환.
    동기 함수 — to_thread로 호출.
    권한 없는 폴더는 조용히 건너뜁니다.
    """
    results: list[DocumentMetadata] = []
    dir_path = Path(directory)
    if not dir_path.exists() or not dir_path.is_dir():
        return results

    count = 0
    for root, dirs, files in os.walk(str(dir_path), followlinks=False):
        # 숨김 폴더 건너뜀
        dirs[:] = [d for d in dirs if not d.startswith(".")]
        for fname in files:
            if count >= _MAX_FILES_PER_DIR:
                break
            full_path = os.path.join(root, fname)
            item_id = str(uuid.uuid5(uuid.NAMESPACE_URL, full_path))
            meta = extract_metadata(full_path, item_id)
            if meta is not None:
                results.append(meta)
                count += 1
        if count >= _MAX_FILES_PER_DIR:
            break
    return results


# ─── 공개 API ─────────────────────────────────────────────────────


class LocalIndexer:
    """
    로컬 파일 색인기.

    사용:
        indexer = LocalIndexer()
        await indexer.scan_and_index()
        results = await indexer.search("견적서")
    """

    def __init__(self, db_path: Optional[Path] = None, scan_dirs: Optional[list[str]] = None):
        self._db_path = db_path or _DB_PATH
        self._scan_dirs = scan_dirs or DEFAULT_SCAN_DIRS
        _init_db(self._db_path)

    async def scan_and_index(self, directories: Optional[list[str]] = None) -> int:
        """
        지정 디렉토리(또는 기본 목록)를 색인하고 저장된 파일 수를 반환합니다.
        asyncio.to_thread()로 이벤트 루프를 블록하지 않습니다.
        """
        dirs = directories or self._scan_dirs
        all_records: list[DocumentMetadata] = []

        for directory in dirs:
            records = await asyncio.to_thread(_scan_directory_sync, directory)
            all_records.extend(records)

        saved = await asyncio.to_thread(_upsert_all_sync, all_records, self._db_path)
        return saved

    async def search(self, query: str, limit: int = 20) -> list[dict]:
        """
        title/summary LIKE 검색.
        빈 query → 최근 항목 반환.
        """
        return await asyncio.to_thread(_search_sync, query, limit, self._db_path)

    async def count(self) -> int:
        """색인된 총 항목 수를 반환합니다."""
        def _count(db_path: Path) -> int:
            conn = sqlite3.connect(str(db_path))
            try:
                return conn.execute("SELECT COUNT(*) FROM local_index").fetchone()[0]
            finally:
                conn.close()
        return await asyncio.to_thread(_count, self._db_path)
