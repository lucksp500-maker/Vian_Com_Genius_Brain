"""
QA-02: 정상 흐름 2 — 거부 후 Audit
실증 항목:
  - POST /api/v1/action-spec/{id}/reject → execution_state=user_rejected
  - audit_ledger approval_result="rejected"
  - _store에서 spec 상태 변경 확인
"""
import sqlite3
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.core.commandos.hud_bridge import _store

_DB_PATH = Path(__file__).parent.parent.parent / "data" / "audit_ledger.sqlite"


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_qa02_reject_sets_state_rejected(client):
    """QA-02-A: reject → execution_state=user_rejected."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "요약해줘"},
    )
    assert resp.status_code == 200
    action_id = resp.json()["action_id"]

    reject_resp = await client.post(f"/api/v1/action-spec/{action_id}/reject")
    assert reject_resp.status_code == 200
    assert reject_resp.json()["execution_state"] == "user_rejected"


@pytest.mark.asyncio
async def test_qa02_reject_creates_audit_record(client):
    """QA-02-B: reject → audit_ledger에 approval_result=rejected 기록."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "현재 페이지 북마크해줘"},
    )
    assert resp.status_code == 200
    action_id = resp.json()["action_id"]

    await client.post(f"/api/v1/action-spec/{action_id}/reject")

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
    assert row["approval_result"] == "rejected", (
        f"approval_result 기대: rejected, 실제: {row['approval_result']}"
    )


@pytest.mark.asyncio
async def test_qa02_reject_updates_store_state(client):
    """QA-02-C: reject 후 _store에서 spec 상태가 user_rejected로 변경됨."""
    resp = await client.post(
        "/api/v1/action-spec/create",
        json={"raw_input": "탭 닫아줘"},
    )
    assert resp.status_code == 200
    action_id = resp.json()["action_id"]

    await client.post(f"/api/v1/action-spec/{action_id}/reject")

    # 메모리 _store에서 직접 확인
    spec = _store.get(action_id)
    assert spec is not None, f"_store에 action_id={action_id} 없음"
    assert spec.execution_state == "user_rejected", (
        f"execution_state 기대: user_rejected, 실제: {spec.execution_state}"
    )
