"""
WO-003 — hud_bridge.py 테스트
HUD ↔ Web App action_id 발급/조회/실행 흐름 검증
"""
import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_create_action_spec_returns_action_id(client):
    """POST /api/v1/action-spec/create → action_id 반환."""
    resp = await client.post("/api/v1/action-spec/create", json={"raw_input": "이 PDF 요약해줘"})
    assert resp.status_code == 200
    data = resp.json()
    assert "action_id" in data
    assert len(data["action_id"]) == 36  # UUID 형식


@pytest.mark.asyncio
async def test_create_returns_risk_level(client):
    """생성 응답에 risk_level 포함 확인."""
    resp = await client.post("/api/v1/action-spec/create", json={"raw_input": "요약해줘"})
    assert resp.status_code == 200
    data = resp.json()
    assert "risk_level" in data
    assert data["risk_level"] in ("none", "low", "medium", "high")


@pytest.mark.asyncio
async def test_create_returns_guard_result(client):
    """생성 응답에 guard_result 포함 확인."""
    resp = await client.post("/api/v1/action-spec/create", json={"raw_input": "번역해줘"})
    assert resp.status_code == 200
    data = resp.json()
    assert "guard_result" in data
    assert data["guard_result"] in ("allow", "deny", "ask")


@pytest.mark.asyncio
async def test_high_risk_returns_preview_url(client):
    """고위험 명령은 preview_url 반환 확인."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "이 파일 삭제해줘"},
    )
    assert resp.status_code == 200
    data = resp.json()
    # high risk → preview_url이 있어야 함
    if data["risk_level"] == "high":
        assert data.get("preview_url") is not None
        assert data["action_id"] in data["preview_url"]


@pytest.mark.asyncio
async def test_get_action_spec_by_id(client):
    """GET /api/v1/action-spec/{action_id} → spec + preview 반환."""
    # 먼저 생성
    create_resp = await client.post(
        "/api/v1/action-spec/create", json={"raw_input": "현재 탭 저장해줘"}
    )
    action_id = create_resp.json()["action_id"]

    # 조회
    get_resp = await client.get(f"/api/v1/action-spec/{action_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert "spec" in data
    assert "preview" in data
    assert data["spec"]["action_id"] == action_id


@pytest.mark.asyncio
async def test_get_nonexistent_action_returns_404(client):
    """존재하지 않는 action_id → 404."""
    resp = await client.get("/api/v1/action-spec/nonexistent-id-xyz")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_execute_approved_action(client):
    """승인 후 execute → execution_state=user_approved."""
    create_resp = await client.post(
        "/api/v1/action-spec/create", json={"raw_input": "감사 로그 보여줘"}
    )
    action_id = create_resp.json()["action_id"]
    guard_result = create_resp.json().get("guard_result")

    # deny가 아닌 경우만 실행 가능
    if guard_result != "deny":
        exec_resp = await client.post(f"/api/v1/action-spec/{action_id}/execute")
        assert exec_resp.status_code == 200
        assert exec_resp.json()["execution_state"] == "user_approved"


@pytest.mark.asyncio
async def test_reject_action(client):
    """사용자 취소 → execution_state=user_rejected."""
    create_resp = await client.post(
        "/api/v1/action-spec/create", json={"raw_input": "요약해줘"}
    )
    action_id = create_resp.json()["action_id"]

    reject_resp = await client.post(f"/api/v1/action-spec/{action_id}/reject")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["execution_state"] == "user_rejected"
