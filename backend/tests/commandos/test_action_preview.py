"""
WO-003 — action_preview.py 테스트
ActionSpec → preview dict 직렬화 검증
"""
import pytest

from backend.core.commandos.action_spec import ActionSpec, RiskLevel, TargetType
from backend.core.commandos.action_preview import build_preview


def _make_spec(risk_level: RiskLevel, target_type: TargetType, requires_approval: bool = False,
               intent: str = "테스트 의도", raw_input: str = "테스트 입력",
               guard_result: str = "allow") -> ActionSpec:
    spec = ActionSpec(
        raw_input=raw_input,
        intent=intent,
        risk_level=risk_level,
        target_type=target_type,
        requires_approval=requires_approval,
    )
    spec.guard_result = guard_result
    return spec


def test_preview_contains_required_fields():
    """preview dict에 필수 필드 모두 포함 확인."""
    spec = _make_spec(RiskLevel.none, TargetType.file)
    preview = build_preview(spec)
    required = {
        "action_id", "intent", "raw_input", "target_display",
        "risk_display", "requires_approval", "guard_result",
        "execution_steps", "safety_warnings",
    }
    for field in required:
        assert field in preview, f"preview에 '{field}' 없음"


def test_preview_action_id_matches():
    """preview.action_id == spec.action_id."""
    spec = _make_spec(RiskLevel.low, TargetType.browser_tab)
    preview = build_preview(spec)
    assert preview["action_id"] == spec.action_id


def test_high_risk_preview_shows_danger():
    """high risk → risk_display.color='error'."""
    spec = _make_spec(RiskLevel.high, TargetType.file, requires_approval=True)
    preview = build_preview(spec)
    assert preview["risk_display"]["color"] == "error"
    assert preview["requires_approval"] is True


def test_none_risk_preview_shows_safe():
    """none risk → risk_display.color='success'."""
    spec = _make_spec(RiskLevel.none, TargetType.file)
    preview = build_preview(spec)
    assert preview["risk_display"]["color"] == "success"


def test_execution_steps_not_empty():
    """execution_steps가 비어있지 않음."""
    spec = _make_spec(RiskLevel.low, TargetType.browser_tab)
    preview = build_preview(spec)
    assert len(preview["execution_steps"]) >= 2


def test_high_risk_has_approval_step():
    """high risk → '사용자 승인 대기' 단계 포함."""
    spec = _make_spec(RiskLevel.high, TargetType.file, requires_approval=True,
                      guard_result="ask")
    preview = build_preview(spec)
    steps = preview["execution_steps"]
    labels = [s["label"] for s in steps]
    assert any("승인" in label for label in labels), f"승인 단계 없음: {labels}"


def test_safety_warnings_for_high_risk():
    """high risk → safety_warnings 1건 이상."""
    spec = _make_spec(RiskLevel.high, TargetType.file, requires_approval=True)
    preview = build_preview(spec)
    assert len(preview["safety_warnings"]) >= 1


def test_safety_warnings_for_none_risk_empty():
    """none risk, file target → safety_warnings 비어있음."""
    spec = _make_spec(RiskLevel.none, TargetType.file)
    preview = build_preview(spec)
    assert preview["safety_warnings"] == []


def test_target_display_browser_tab():
    """target_type=browser_tab → '현재 브라우저 탭' 표시."""
    spec = _make_spec(RiskLevel.low, TargetType.browser_tab)
    preview = build_preview(spec)
    assert "브라우저" in preview["target_display"]


def test_preview_uses_intent_field():
    """intent 있으면 intent 사용, 없으면 raw_input fallback."""
    spec_with_intent = _make_spec(RiskLevel.none, TargetType.file, intent="문서 요약")
    assert build_preview(spec_with_intent)["intent"] == "문서 요약"

    spec_no_intent = ActionSpec(raw_input="요약해줘")
    preview_no_intent = build_preview(spec_no_intent)
    assert preview_no_intent["intent"] == "요약해줘"
