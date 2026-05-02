"""
local_index_router.py — WO-004
FastAPI 라우터: 로컬 파일 색인 + 검색 + 미리보기 API 엔드포인트.
"""
from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel

from backend.core.indexer.local_indexer import LocalIndexer
from backend.core.preview.local_preview_engine import LocalPreviewEngine

router = APIRouter(prefix="/api/v1/local-index", tags=["local-index"])
preview_router = APIRouter(prefix="/api/v1/local-preview", tags=["local-preview"])

# 앱 수명 내 단일 인스턴스 (SQLite는 연결마다 새로 열기)
_indexer = LocalIndexer()
_preview_engine = LocalPreviewEngine()


class IndexResponse(BaseModel):
    indexed_count: int
    message: str


class SearchResponse(BaseModel):
    query: str
    results: list[dict]
    count: int


class CountResponse(BaseModel):
    count: int


@router.post("/index", response_model=IndexResponse)
async def index_local_files() -> IndexResponse:
    """기본 디렉토리(Downloads, Documents, Desktop)를 색인합니다."""
    count = await _indexer.scan_and_index()
    return IndexResponse(
        indexed_count=count,
        message=f"{count}개 파일이 색인됐습니다.",
    )


@router.get("/search", response_model=SearchResponse)
async def search_local_files(
    q: str = Query(default="", description="검색 쿼리"),
    limit: int = Query(default=20, ge=1, le=100),
) -> SearchResponse:
    """로컬 색인에서 파일을 검색합니다. q가 비면 최근 항목을 반환합니다."""
    results = await _indexer.search(q, limit=limit)
    return SearchResponse(query=q, results=results, count=len(results))


@router.get("/count", response_model=CountResponse)
async def count_indexed_files() -> CountResponse:
    """색인된 총 파일 수를 반환합니다."""
    count = await _indexer.count()
    return CountResponse(count=count)


@preview_router.get("")
async def preview_file(
    path: str = Query(description="미리보기할 파일의 절대 경로"),
) -> dict:
    """로컬 파일 미리보기 데이터를 반환합니다."""
    result = await _preview_engine.preview_file(path)
    return result.to_dict()
