"""
QA-06: 동시성 시나리오
실증 항목:
  - asyncio.gather로 동시 10개 ActionSpec 생성 요청
  - _store dict에 모두 저장 확인 (race condition 없음)
  - audit_ledger SQLite 동시 쓰기 안전성 (database is locked 에러 없음)
"""
import asyncio
import sqlite3
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.core.commandos.hud_bridge import _store

_DB_PATH = Path(__file__).parent.parent.parent / "data" / "audit_ledger.sqlite"

_CONCURRENCY = 10


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_qa06_concurrent_create_all_stored(client):
    """QA-06-A: 동시 10개 create → _store에 모두 저장 (race condition 없음)."""
    before_ids = set(_store.keys())

    async def create_one(i: int) -> str:
        resp = await client.post(
            "/api/v1/action-spec/create",
            json={"raw_input": f"동시성 테스트 명령 {i}"},
        )
        assert resp.status_code == 200, f"create #{i} 실패: {resp.status_code}"
        return resp.json()["action_id"]

    action_ids = await asyncio.gather(*[create_one(i) for i in range(_CONCURRENCY)])

    # 고유 ID 수 확인
    assert len(set(action_ids)) == _CONCURRENCY, (
        f"ID 충돌 발생 — UUID 중복 또는 race condition: {action_ids}"
    )

    # _store에 모두 저장됐는지 확인
    after_ids = set(_store.keys())
    new_ids = after_ids - before_ids
    for aid in action_ids:
        assert aid in new_ids, (
            f"action_id={aid}가 _store에 없음 — 동시 쓰기 race condition 가능성"
        )


@pytest.mark.asyncio
async def test_qa06_concurrent_audit_no_database_locked(client):
    """QA-06-B: 동시 execute/reject → SQLite 'database is locked' 에러 없음."""
    # 먼저 10개 spec 생성
    async def create_one(i: int) -> dict:
        resp = await client.post(
            "/api/v1/action-spec/create",
            json={"raw_input": f"동시 Audit 테스트 {i}"},
        )
        return resp.json()

    specs = await asyncio.gather(*[create_one(i) for i in range(_CONCURRENCY)])

    # 각 spec에 대해 execute 또는 reject 동시 실행
    async def act_on_spec(spec: dict, i: int):
        action_id = spec["action_id"]
        guard_result = spec.get("guard_result", "allow")
        if guard_result == "deny":
            resp = await client.post(f"/api/v1/action-spec/{action_id}/reject")
        else:
            resp = await client.post(f"/api/v1/action-spec/{action_id}/execute")
        assert resp.status_code == 200, (
            f"act #{i} 실패 (action_id={action_id}): {resp.status_code} — "
            "SQLite 'database is locked' 또는 기타 오류"
        )
        return action_id

    acted_ids = await asyncio.gather(*[act_on_spec(s, i) for i, s in enumerate(specs)])

    # audit_ledger에 기록 확인
    if not _DB_PATH.exists():
        pytest.skip("audit_ledger.sqlite 없음 — DB 기록 검증 불가")

    conn = sqlite3.connect(str(_DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        for aid in acted_ids:
            rows = conn.execute(
                "SELECT COUNT(*) as cnt FROM audit_ledger WHERE action_spec_id = ?",
                (aid,),
            ).fetchone()
            assert rows["cnt"] >= 1, (
                f"action_id={aid}의 audit 기록 없음 — 동시 SQLite 쓰기 실패 가능성"
            )
    finally:
        conn.close()


@pytest.mark.asyncio
async def test_qa06_concurrent_ids_are_unique(client):
    """QA-06-C: 동시 생성된 action_id들이 모두 고유함 (UUID collision 없음)."""
    async def get_id(i: int) -> str:
        resp = await client.post(
            "/api/v1/action-spec/create",
            json={"raw_input": f"UUID 충돌 테스트 {i}"},
        )
        return resp.json()["action_id"]

    ids = await asyncio.gather(*[get_id(i) for i in range(_CONCURRENCY)])
    assert len(ids) == len(set(ids)), (
        f"UUID 충돌 발생: {[x for x in ids if ids.count(x) > 1]}"
    )
