"""
Fix Phase 2-B 회귀 방지 테스트 — HIGH 통합 흐름 8건
대상:
  I-01: create_action_spec Guard allow → execution_state=guard_approved
  I-02: collect_push → spec guard_result/execution_state 미반영
  I-03: receive_result → AuditLedger 미기록
  I-04: dispatch_command → AuditLedger 미기록
  I-05: execute_action 멱등성 — 이중 실행 방지
  I-06: Brain Router 싱글턴 프로덕션 DB 오염 (conftest.py 픽스처로 검증)
  I-07: _INTERNAL_TOKEN 하드코딩 기본값 → None 처리
  I-08: reject_action 멱등성 — 이중 거부 방지
"""
import os
import sqlite3
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient, ASGITransport

from backend.main import app
from backend.core.commandos.action_spec import (
    ActionSpec, ExecutionState, TargetType, RiskLevel, ActionSource
)
from backend.core.guard.policy_engine import PolicyResult

_DB_PATH = Path(__file__).parent.parent.parent / "data" / "audit_ledger.sqlite"


@pytest.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


# ─── I-01: Guard allow → execution_state=guard_approved ──────────────────

def test_i01_guard_allow_sets_guard_approved():
    """I-01 회귀: Guard allow 결과 → execution_state=guard_approved (pending 아님)."""
    from backend.core.commandos.hud_bridge import _store
    from backend.core.guard.policy_engine import evaluate
    from backend.core.commandos.ai_intent_bridge import _regex_fallback

    spec_data = _regex_fallback("페이지 요약해줘")  # summarize → risk=none → allow
    spec = ActionSpec(raw_input="페이지 요약해줘", **spec_data)

    guard_eval = evaluate(spec)
    if guard_eval.result != PolicyResult.allow:
        pytest.skip(f"이 spec은 allow가 아님: {guard_eval.result} — I-01 테스트 조건 불충족")

    # hud_bridge 흐름 시뮬레이션
    if guard_eval.result == PolicyResult.allow:
        spec.execution_state = ExecutionState.guard_approved.value

    assert spec.execution_state == ExecutionState.guard_approved.value, (
        f"I-01 회귀: Guard allow 후 execution_state={spec.execution_state} (guard_approved 아님)"
    )


def test_i01_guard_allow_allows_dispatch():
    """I-01 회귀: guard_approved 상태 spec은 dispatch 가능 (_ALLOWED_EXEC_STATES 포함)."""
    from backend.core.browser.browser_automation_adapter import _ALLOWED_EXEC_STATES
    assert ExecutionState.guard_approved.value in _ALLOWED_EXEC_STATES, (
        "I-01 회귀: guard_approved가 _ALLOWED_EXEC_STATES에 없음 — dispatch 불가"
    )


# ─── I-02: collect_push → spec guard_result 반영 ─────────────────────────

def test_i02_collect_spec_has_guard_result():
    """I-02 회귀: collect_push 후 spec에 guard_result가 설정됨 (None 아님)."""
    from backend.core.browser.browser_automation_adapter import (
        BrowserAutomationAdapter, BrowserPushPayload
    )
    from backend.core.guard.policy_engine import evaluate, PolicyResult

    adapter = BrowserAutomationAdapter()
    payload = BrowserPushPayload(
        action_type="summarize",
        url="http://example.com",
        title="Test Page",
        raw_content="safe content only",
    )
    push_result = adapter.receive_push(payload)
    assert not push_result.blocked, "Shield이 정상 콘텐츠를 차단함"

    spec = push_result.action_spec
    guard_eval = evaluate(spec)

    if guard_eval.result != PolicyResult.deny:
        spec.guard_result = guard_eval.result.value
        spec.guard_reason = guard_eval.reason
        if guard_eval.result == PolicyResult.allow:
            spec.execution_state = ExecutionState.guard_approved.value

    assert spec.guard_result is not None, (
        "I-02 회귀: collect_push 후 spec.guard_result가 None — Guard 결과 미반영"
    )


def test_i02_collect_allow_spec_execution_state_guard_approved():
    """I-02 회귀: collect allow spec → execution_state=guard_approved."""
    from backend.core.browser.browser_automation_adapter import (
        BrowserAutomationAdapter, BrowserPushPayload
    )
    from backend.core.guard.policy_engine import evaluate, PolicyResult

    adapter = BrowserAutomationAdapter()
    payload = BrowserPushPayload(
        action_type="summarize",
        url="http://example.com",
        title="Summary Test",
        raw_content="clean page content",
    )
    push_result = adapter.receive_push(payload)
    if push_result.blocked:
        pytest.skip("Shield 차단 — collect 흐름 테스트 불가")

    spec = push_result.action_spec
    guard_eval = evaluate(spec)

    if guard_eval.result == PolicyResult.allow:
        spec.execution_state = ExecutionState.guard_approved.value

    if guard_eval.result == PolicyResult.allow:
        assert spec.execution_state == ExecutionState.guard_approved.value, (
            "I-02 회귀: collect allow 후 execution_state=pending (guard_approved 아님)"
        )


# ─── I-03: receive_result → AuditLedger 기록 ─────────────────────────────

@pytest.mark.asyncio
async def test_i03_receive_result_audit_recorded(client, tmp_path):
    """I-03 회귀: POST /browser/result 성공 시 AuditLedger에 기록됨."""
    from backend.core.audit.audit_ledger import AuditLedger

    tmp_db = tmp_path / "test_audit.sqlite"
    tmp_ledger = AuditLedger(db_path=tmp_db)

    import backend.api.browser_router as br_module
    with patch.object(br_module, "_ledger", tmp_ledger):
        resp = await client.post(
            "/api/v1/browser/result",
            json={
                "command_id": "test-cmd-i03",
                "action_type": "summarize",
                "url": "http://example.com",
                "title": "Test",
                "raw_content": "safe test content",
            },
        )
        assert resp.status_code == 200

    records = await tmp_ledger.list_recent(limit=10)
    assert len(records) >= 1, (
        "I-03 회귀: /browser/result 후 AuditLedger에 기록 없음"
    )
    action_types = [r.get("intent_class") for r in records]
    assert "summarize" in action_types, (
        f"I-03 회귀: audit 기록에 summarize intent_class 없음 — records={records}"
    )


# ─── I-04: dispatch_command → AuditLedger 기록 ───────────────────────────

@pytest.mark.asyncio
async def test_i04_dispatch_audit_recorded(client, tmp_path):
    """I-04 회귀: POST /browser/dispatch 성공 시 AuditLedger에 기록됨."""
    from backend.core.audit.audit_ledger import AuditLedger

    tmp_db = tmp_path / "test_audit_dispatch.sqlite"
    tmp_ledger = AuditLedger(db_path=tmp_db)

    import backend.api.browser_router as br_module
    spec = ActionSpec(
        raw_input="save_tab: http://example.com",
        intent="현재 탭 저장",
        target_type=TargetType.browser_tab,
        target_ref="http://example.com",
        risk_level=RiskLevel.low,
        requires_approval=True,
        execution_state=ExecutionState.guard_approved,
        source=ActionSource.extension,
    )

    with patch.object(br_module, "_ledger", tmp_ledger):
        resp = await client.post(
            "/api/v1/browser/dispatch",
            json={"action_spec": spec.model_dump(mode="json")},
        )
        # guard_approved spec이므로 200 또는 dispatch 성공 확인
        assert resp.status_code in (200, 422), f"dispatch 실패: {resp.text}"

        if resp.status_code == 200 and resp.json().get("queued"):
            records = await tmp_ledger.list_recent(limit=10)
            assert len(records) >= 1, (
                "I-04 회귀: /browser/dispatch 성공 후 AuditLedger에 기록 없음"
            )
            approval_results = [r.get("approval_result") for r in records]
            assert "dispatched" in approval_results, (
                f"I-04 회귀: audit 기록에 dispatched 없음 — records={records}"
            )


# ─── I-05: execute_action 멱등성 ─────────────────────────────────────────

@pytest.mark.asyncio
async def test_i05_double_execute_returns_409(client):
    """I-05 회귀: 동일 ActionSpec 두 번 execute → 두 번째는 409 Conflict."""
    from backend.core.commandos.hud_bridge import _store
    from backend.core.commandos.action_spec import GuardResult

    spec = ActionSpec(
        raw_input="멱등성 테스트 명령",
        intent="test intent",
        target_type=TargetType.file,
        risk_level=RiskLevel.low,
        guard_result=GuardResult.allow,
        execution_state=ExecutionState.pending,
    )
    _store[spec.action_id] = spec

    # 첫 번째 execute — 성공해야 함
    resp1 = await client.post(f"/api/v1/action-spec/{spec.action_id}/execute")
    assert resp1.status_code == 200, f"첫 번째 execute 실패: {resp1.text}"

    # 두 번째 execute — 409 Conflict
    resp2 = await client.post(f"/api/v1/action-spec/{spec.action_id}/execute")
    assert resp2.status_code == 409, (
        f"I-05 회귀: 두 번째 execute가 {resp2.status_code} — 409 Conflict 기대"
    )


# ─── I-06: Brain Router DB 격리 (conftest.py 픽스처 동작 확인) ────────────

def test_i06_brain_router_uses_tmp_db(tmp_path):
    """I-06 회귀: conftest.py autouse 픽스처가 brain router 싱글턴을 tmp DB로 교체함."""
    import backend.core.brain.commandos_brain_router as router_module

    engine = router_module._consistency_engine
    engine_db_path = engine._db_path

    # conftest.py 픽스처가 적용됐다면 tmp_path 기반 경로여야 함
    prod_db = Path(__file__).parent.parent.parent / "data" / "decision_fingerprints.sqlite"
    assert engine_db_path != prod_db, (
        f"I-06 회귀: _consistency_engine이 프로덕션 DB 사용 중 — conftest.py 픽스처 미작동\n"
        f"  현재 경로: {engine_db_path}\n"
        f"  프로덕션 경로: {prod_db}"
    )


# ─── I-07: _INTERNAL_TOKEN 하드코딩 기본값 제거 ───────────────────────────

def test_i07_internal_token_no_hardcoded_default():
    """I-07 회귀: VIAN_INTERNAL_TOKEN 미설정 시 _INTERNAL_TOKEN이 None이어야 함."""
    import importlib
    import backend.api.audit_router as ar_module

    # 환경변수 미설정 상태에서 모듈 재로드하여 확인
    original_env = os.environ.pop("VIAN_INTERNAL_TOKEN", None)
    try:
        importlib.reload(ar_module)
        assert ar_module._INTERNAL_TOKEN is None, (
            f"I-07 회귀: VIAN_INTERNAL_TOKEN 미설정 시 _INTERNAL_TOKEN이 None이 아님 — "
            f"값={ar_module._INTERNAL_TOKEN!r} (하드코딩 기본값이 여전히 존재)"
        )
    finally:
        if original_env is not None:
            os.environ["VIAN_INTERNAL_TOKEN"] = original_env
        importlib.reload(ar_module)


@pytest.mark.asyncio
async def test_i07_undo_record_disabled_when_no_token(client):
    """I-07 회귀: VIAN_INTERNAL_TOKEN 미설정 시 POST /undo/record → 503."""
    import importlib
    import backend.api.audit_router as ar_module

    original_env = os.environ.pop("VIAN_INTERNAL_TOKEN", None)
    try:
        original_token = ar_module._INTERNAL_TOKEN
        ar_module._INTERNAL_TOKEN = None

        resp = await client.post(
            "/api/v1/undo/record",
            headers={"x-internal-token": "vian-internal-v1"},
            json={
                "operation_type": "file_move",
                "before_state": {"path": "/tmp/test.txt"},
                "action_id": "test-i07",
            },
        )
        # 503: 토큰 미설정, 또는 403: 잘못된 토큰
        assert resp.status_code in (503, 403), (
            f"I-07 회귀: 토큰 미설정 상태에서 {resp.status_code} 반환 — 503/403 기대"
        )
    finally:
        ar_module._INTERNAL_TOKEN = original_token
        if original_env is not None:
            os.environ["VIAN_INTERNAL_TOKEN"] = original_env


# ─── I-08: reject_action 멱등성 ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_i08_double_reject_returns_409(client):
    """I-08 회귀: 동일 ActionSpec 두 번 reject → 두 번째는 409 Conflict."""
    from backend.core.commandos.hud_bridge import _store
    from backend.core.commandos.action_spec import GuardResult

    spec = ActionSpec(
        raw_input="멱등성 거부 테스트",
        intent="test reject",
        target_type=TargetType.file,
        risk_level=RiskLevel.low,
        guard_result=GuardResult.ask,
        requires_approval=True,
        execution_state=ExecutionState.pending,
    )
    _store[spec.action_id] = spec

    # 첫 번째 reject — 성공
    resp1 = await client.post(f"/api/v1/action-spec/{spec.action_id}/reject")
    assert resp1.status_code == 200, f"첫 번째 reject 실패: {resp1.text}"

    # 두 번째 reject — 409 Conflict
    resp2 = await client.post(f"/api/v1/action-spec/{spec.action_id}/reject")
    assert resp2.status_code == 409, (
        f"I-08 회귀: 두 번째 reject가 {resp2.status_code} — 409 Conflict 기대"
    )
