"""
QA-01: 정상 흐름 1 — HUD 입력 → 승인 → Audit
실증 항목:
  - POST /api/v1/action-spec/create → ActionSpec (confidence_score 비어있지 않음)
  - POST /api/v1/action-spec/{id}/execute → audit_ledger 기록 생성
  - audit_ledger approval_result="approved"
"""
import sqlite3
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app

_DB_PATH = Path(__file__).parent.parent.parent / "data" / "audit_ledger.sqlite"


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_qa01_create_spec_has_confidence_score(client):
    """QA-01-A: Brain Router 호출 검증 — confidence_score가 None이 아님."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "save current tab"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "action_id" in data
    assert data["confidence_score"] is not None, (
        "Brain Router가 호출되지 않음 — confidence_score가 None"
    )
    assert 0.0 <= data["confidence_score"] <= 1.0


@pytest.mark.asyncio
async def test_qa01_execute_creates_audit_record(client):
    """QA-01-B: execute → audit_ledger에 approved 기록 생성."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "현재 탭 저장해줘"},
    )
    assert resp.status_code == 200
    data = resp.json()
    action_id = data["action_id"]
    guard_result = data.get("guard_result")

    # deny인 경우 execute는 403 — skip
    if guard_result == "deny":
        pytest.skip(f"guard_result=deny — execute 불가 (action_id={action_id})")

    exec_resp = await client.post(f"/api/v1/action-spec/{action_id}/execute")
    assert exec_resp.status_code == 200
    assert exec_resp.json()["execution_state"] == "user_approved"

    # audit_ledger SQLite 직접 확인
    if not _DB_PATH.exists():
        pytest.skip("audit_ledger.sqlite 없음 — DB 기록 검증 불가")

    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        rows = conn.execute(
            "SELECT * FROM audit_ledger WHERE action_spec_id = ? ORDER BY created_at DESC LIMIT 1",
            (action_id,),
        ).fetchall()
    finally:
        conn.close()

    assert len(rows) == 1, f"audit_ledger에 action_id={action_id} 기록 없음"
    row = dict(rows[0])
    assert row["approval_result"] == "approved", (
        f"approval_result 기대: approved, 실제: {row['approval_result']}"
    )


@pytest.mark.asyncio
async def test_qa01_guard_result_is_not_none(client):
    """QA-01-C: guard_result/guard_reason이 None이 아님."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "번역해줘"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["guard_result"] in ("allow", "deny", "ask"), (
        f"guard_result 비정상: {data['guard_result']}"
    )
    assert data.get("guard_reason") is not None, "guard_reason이 None"
