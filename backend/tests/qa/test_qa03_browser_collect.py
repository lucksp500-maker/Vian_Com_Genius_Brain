"""
QA-03: 정상 흐름 3 — Browser collect
실증 항목:
  - POST /api/v1/browser/collect → 응답에 action_id 포함
  - spec이 hud_bridge._store에 저장됨 확인
  - preview_url 호출 시 정상 응답 (404 아님)
"""
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.core.commandos.hud_bridge import _store


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


_VALID_COLLECT_PAYLOAD = {
    "action_type": "summarize",
    "url": "https://example.com/article",
    "title": "Test Article",
    "raw_content": "This is normal article content without any injection.",
    "meta_description": "A test article",
    "word_count": 100,
}


@pytest.mark.asyncio
async def test_qa03_collect_returns_action_id(client):
    """QA-03-A: collect → action_id 포함 응답."""
    resp = await client.post("/api/v1/browser/collect", json=_VALID_COLLECT_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    assert not data["blocked"], f"차단됨: {data['block_reason']}"
    assert data["action_id"] is not None, "action_id가 None"


@pytest.mark.asyncio
async def test_qa03_collect_spec_stored_in_hud_store(client):
    """QA-03-B: collect로 생성된 spec이 hud_bridge._store에 저장됨 (C-11 Fix 검증)."""
    resp = await client.post("/api/v1/browser/collect", json=_VALID_COLLECT_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()

    action_id = data.get("action_id")
    assert action_id is not None

    # _store에서 직접 확인
    spec = _store.get(action_id)
    assert spec is not None, (
        f"C-11 Fix 회귀: action_id={action_id}가 _store에 없음 "
        "— collect 후 preview_url 접근 시 404 발생 가능"
    )


@pytest.mark.asyncio
async def test_qa03_preview_url_accessible_after_collect(client):
    """QA-03-C: collect 후 preview_url → GET /api/v1/action-spec/{id} 404 아님."""
    resp = await client.post("/api/v1/browser/collect", json=_VALID_COLLECT_PAYLOAD)
    assert resp.status_code == 200
    data = resp.json()
    action_id = data.get("action_id")
    assert action_id is not None

    get_resp = await client.get(f"/api/v1/action-spec/{action_id}")
    assert get_resp.status_code == 200, (
        f"collect 후 action-spec 조회 실패: {get_resp.status_code} "
        "— _store 등록 누락 또는 C-11 Fix 회귀"
    )
    spec_data = get_resp.json()
    assert spec_data["spec"]["action_id"] == action_id
