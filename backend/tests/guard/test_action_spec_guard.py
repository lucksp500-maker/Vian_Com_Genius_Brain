"""
WO-002 — Guard Policy Engine 테스트
삭제/외부전송/폼제출 명령이 ask 또는 deny로 차단되는지 검증합니다.
"""
import pytest

from backend.core.commandos.action_spec import ActionSpec, RiskLevel, TargetType
from backend.core.guard.policy_engine import PolicyResult, evaluate


def _make_spec(risk_level: RiskLevel, target_type: TargetType = TargetType.file,
               requires_approval: bool = False) -> ActionSpec:
    """테스트용 ActionSpec 생성 헬퍼."""
    return ActionSpec(
        raw_input="테스트 명령",
        risk_level=risk_level,
        target_type=target_type,
        requires_approval=requires_approval,
    )


# ────────────────────────────────────────────
# deny 케이스
# ────────────────────────────────────────────

def test_unknown_target_with_approval_is_denied():
    """target_type=unknown + requires_approval=True → deny."""
    spec = _make_spec(
        risk_level=RiskLevel.high,
        target_type=TargetType.unknown,
        requires_approval=True,
    )
    result = evaluate(spec)
    assert result.result == PolicyResult.deny


# ────────────────────────────────────────────
# ask 케이스 (차단 → 승인 대기)
# ────────────────────────────────────────────

def test_high_risk_is_asked():
    """risk_level=high → ask."""
    spec = _make_spec(risk_level=RiskLevel.high, requires_approval=True)
    result = evaluate(spec)
    assert result.result == PolicyResult.ask


def test_delete_action_is_blocked():
    """삭제 명령 (high risk + requires_approval) → ask."""
    spec = ActionSpec(
        raw_input="이 파일 삭제해줘",
        risk_level=RiskLevel.high,
        target_type=TargetType.file,
        requires_approval=True,
        intent="파일 삭제",
    )
    result = evaluate(spec)
    assert result.result in (PolicyResult.ask, PolicyResult.deny)
    assert result.requires_approval is True


def test_send_external_is_blocked():
    """외부 전송 (high risk) → ask."""
    spec = ActionSpec(
        raw_input="현재 탭 내용 외부로 전송해줘",
        risk_level=RiskLevel.high,
        target_type=TargetType.url,
        requires_approval=True,
        intent="외부 전송",
    )
    result = evaluate(spec)
    assert result.result in (PolicyResult.ask, PolicyResult.deny)


def test_form_submit_is_blocked():
    """폼 제출 (high risk) → ask."""
    spec = ActionSpec(
        raw_input="이 폼 제출해줘",
        risk_level=RiskLevel.high,
        target_type=TargetType.browser_tab,
        requires_approval=True,
        intent="폼 제출",
    )
    result = evaluate(spec)
    assert result.result in (PolicyResult.ask, PolicyResult.deny)


def test_medium_risk_is_asked():
    """risk_level=medium → ask."""
    spec = _make_spec(risk_level=RiskLevel.medium)
    result = evaluate(spec)
    assert result.result == PolicyResult.ask


def test_requires_approval_flag_triggers_ask():
    """requires_approval=True이면 risk_level 무관하게 ask."""
    spec = ActionSpec(
        raw_input="명시적 승인 필요 명령",
        risk_level=RiskLevel.low,
        target_type=TargetType.file,
        requires_approval=True,
    )
    result = evaluate(spec)
    assert result.result == PolicyResult.ask


# ────────────────────────────────────────────
# allow 케이스
# ────────────────────────────────────────────

def test_none_risk_is_allowed():
    """risk_level=none → allow."""
    spec = _make_spec(risk_level=RiskLevel.none)
    result = evaluate(spec)
    assert result.result == PolicyResult.allow
    assert result.requires_approval is False


def test_low_risk_is_allowed():
    """risk_level=low → allow."""
    spec = _make_spec(risk_level=RiskLevel.low)
    result = evaluate(spec)
    assert result.result == PolicyResult.allow


def test_summarize_is_allowed():
    """요약 명령 (none risk) → allow."""
    spec = ActionSpec(
        raw_input="이 PDF 요약해줘",
        risk_level=RiskLevel.none,
        target_type=TargetType.file,
        requires_approval=False,
        intent="문서 요약",
    )
    result = evaluate(spec)
    assert result.result == PolicyResult.allow


def test_save_tab_is_allowed():
    """탭 저장 (low risk) → allow."""
    spec = ActionSpec(
        raw_input="현재 탭 저장해줘",
        risk_level=RiskLevel.low,
        target_type=TargetType.browser_tab,
        requires_approval=False,
        intent="탭 아카이브",
    )
    result = evaluate(spec)
    assert result.result == PolicyResult.allow


# ────────────────────────────────────────────
# PolicyEvaluation 필드 검증
# ────────────────────────────────────────────

def test_evaluation_includes_action_id():
    """PolicyEvaluation에 action_id 포함 확인."""
    spec = _make_spec(risk_level=RiskLevel.none)
    result = evaluate(spec)
    assert result.action_id == spec.action_id


def test_evaluation_reason_not_empty():
    """reason 필드가 비어있지 않아야 함."""
    for risk in RiskLevel:
        spec = _make_spec(risk_level=risk)
        result = evaluate(spec)
        assert result.reason, f"{risk}: reason 비어있음"
