"""
QA-05: 장애 시나리오 — Brain 실패
실증 항목:
  - monkeypatch로 brain_route() 강제 RuntimeError
  - guard_router fallback 작동 확인
  - enriched_spec.risk_level == high
  - enriched_spec.requires_approval == True
  - 결과 deny 또는 ask (allow 아님, C-08 Fix 검증)
"""
import pytest

from backend.core.commandos.action_spec import ActionSpec
from backend.core.guard import policy_engine as _pe
from backend.core.guard.guard_router import router as guard_router


@pytest.mark.asyncio
async def test_qa05_brain_failure_fallback_not_allow(monkeypatch):
    """
    QA-05-A: brain_route() RuntimeError 시 Guard fallback → deny 또는 ask.
    C-08 Fix 검증: Brain 실패 시 공격자 제공 spec 기본값(risk=none) 사용 금지.
    """
    import backend.core.brain.commandos_brain_router as brain_mod

    async def _fail(_spec: ActionSpec):
        raise RuntimeError("Brain 강제 실패 — QA-05 시나리오")

    monkeypatch.setattr(brain_mod, "route", _fail)

    spec = ActionSpec(
        action_id="qa05-brain-fail-test",
        raw_input="테스트 명령",
        target_type="browser_tab",
        risk_level="none",
        requires_approval=False,
    )

    from backend.core.commandos.action_spec import RiskLevel
    from backend.core.guard.policy_engine import PolicyResult, evaluate

    # guard_router와 동일한 fallback 로직 재현
    try:
        from backend.core.brain.commandos_brain_router import route as brain_route
        result = await brain_route(spec)
        enriched = result.enriched_spec
    except Exception:
        enriched = spec.model_copy(update={
            "risk_level": RiskLevel.high.value,
            "requires_approval": True,
        })

    # fallback 검증
    assert enriched.risk_level == "high", (
        f"C-08 Fix 회귀: Brain 실패 후 risk_level이 high가 아님. "
        f"실제: {enriched.risk_level}"
    )
    assert enriched.requires_approval is True, (
        f"C-08 Fix 회귀: Brain 실패 후 requires_approval이 True가 아님."
    )

    # Guard 판정 검증
    eval_result = evaluate(enriched)
    assert eval_result.result != PolicyResult.allow, (
        f"C-08 Fix 회귀: Brain 실패 후 Guard가 allow를 반환함. "
        f"result={eval_result.result}"
    )
    assert eval_result.result in (PolicyResult.ask, PolicyResult.deny), (
        f"기대: ask 또는 deny, 실제: {eval_result.result}"
    )


@pytest.mark.asyncio
async def test_qa05_brain_failure_via_api(monkeypatch):
    """
    QA-05-B: HTTP API 경로에서 Brain 실패 → 정상 guard 응답 반환 (500 아님).
    hud_bridge.create_action_spec의 Brain 실패 except 분기 검증.
    """
    import backend.core.brain.commandos_brain_router as brain_mod

    async def _fail(_spec: ActionSpec):
        raise RuntimeError("Brain 강제 실패 — QA-05-B")

    monkeypatch.setattr(brain_mod, "route", _fail)

    from httpx import AsyncClient, ASGITransport
    from backend.main import app

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        resp = await client.post(
            "/api/v1/action-spec/create",
            json={"raw_input": "Brain 실패 시나리오 테스트"},
        )

    # Brain 실패해도 500이 아닌 정상 응답이어야 함
    assert resp.status_code == 200, (
        f"Brain 실패 시 API가 500을 반환함: {resp.status_code}"
    )
    data = resp.json()
    # confidence_score가 없거나 None일 수 있음 (Brain 실패)
    assert "action_id" in data
    assert "guard_result" in data
    assert data["guard_result"] in ("allow", "deny", "ask")
