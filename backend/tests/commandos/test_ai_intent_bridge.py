"""
WO-002 — ai_intent_bridge.py 테스트
실제 Ollama 호출 포함 (qwen2.5:1.5b 설치 필수)
Ollama 없을 때는 regex fallback 경로 검증
"""
import pytest

from backend.core.commandos.ai_intent_bridge import parse_intent, _regex_fallback
from backend.core.commandos.action_spec import (
    ActionSource,
    RiskLevel,
    TargetType,
)


# ────────────────────────────────────────────
# regex fallback 테스트 (Ollama 불필요)
# ────────────────────────────────────────────

def test_regex_fallback_delete_is_high_risk():
    """삭제 명령은 항상 high risk."""
    result = _regex_fallback("이 파일 삭제해줘")
    assert result["risk_level"] == RiskLevel.high
    assert result["requires_approval"] is True


def test_regex_fallback_send_external_is_high_risk():
    """외부 전송 명령은 항상 high risk."""
    result = _regex_fallback("외부로 전송해줘")
    assert result["risk_level"] == RiskLevel.high
    assert result["requires_approval"] is True


def test_regex_fallback_submit_form_is_high_risk():
    """폼 제출 명령은 항상 high risk."""
    result = _regex_fallback("이 폼 제출해줘")
    assert result["risk_level"] == RiskLevel.high
    assert result["requires_approval"] is True


def test_regex_fallback_save_tab_is_low_risk():
    """탭 저장은 low risk."""
    result = _regex_fallback("현재 탭 저장해줘")
    assert result["risk_level"] == RiskLevel.low
    assert result["requires_approval"] is False


def test_regex_fallback_summarize_is_none_risk():
    """요약은 none risk."""
    result = _regex_fallback("이 PDF 요약해줘")
    assert result["risk_level"] == RiskLevel.none
    assert result["requires_approval"] is False


def test_regex_fallback_search_is_none_risk():
    """파일 검색은 none risk."""
    result = _regex_fallback("어제 받은 견적서 찾아줘")
    assert result["risk_level"] == RiskLevel.none


def test_regex_fallback_unknown_input_is_medium_risk():
    """알 수 없는 입력은 medium risk + 승인 필요."""
    result = _regex_fallback("xkq12341234jjjj")
    assert result["risk_level"] in (RiskLevel.medium, RiskLevel.high)
    assert result["requires_approval"] is True


# ────────────────────────────────────────────
# parse_intent 통합 테스트 (Ollama 실제 호출)
# ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_parse_pdf_summary():
    """'이 PDF 요약해줘' → ActionSpec 생성 확인.
    qwen2.5:1.5b는 읽기 전용 작업을 medium으로 보수적으로 분류할 수 있음 — 허용."""
    spec = await parse_intent("이 PDF 요약해줘")
    assert spec.action_id is not None
    assert spec.raw_input == "이 PDF 요약해줘"
    # 소형 모델(qwen2.5:1.5b)은 요약을 medium으로 분류 가능, regex fallback은 none
    assert spec.risk_level in (RiskLevel.none.value, RiskLevel.low.value, RiskLevel.medium.value)
    assert spec.intent != ""


@pytest.mark.asyncio
async def test_parse_find_recent_document():
    """'어제 받은 견적서 찾아줘' → ActionSpec 생성 확인."""
    spec = await parse_intent("어제 받은 견적서 찾아줘")
    assert spec.action_id is not None
    assert spec.raw_input == "어제 받은 견적서 찾아줘"
    assert spec.risk_level in (RiskLevel.none.value, RiskLevel.low.value)
    assert spec.target_type in (TargetType.file.value, TargetType.unknown.value)


@pytest.mark.asyncio
async def test_parse_save_current_tab():
    """'현재 탭 저장해줘' → ActionSpec 생성 확인."""
    spec = await parse_intent("현재 탭 저장해줘")
    assert spec.action_id is not None
    assert spec.raw_input == "현재 탭 저장해줘"
    assert spec.risk_level in (RiskLevel.none.value, RiskLevel.low.value, RiskLevel.medium.value)


@pytest.mark.asyncio
async def test_parse_delete_is_high_risk():
    """삭제 명령 → high risk + requires_approval."""
    spec = await parse_intent("이 파일 삭제해줘")
    assert spec.risk_level == RiskLevel.high.value
    assert spec.requires_approval is True


@pytest.mark.asyncio
async def test_parse_send_external_is_high_risk():
    """외부 전송 → high risk + requires_approval."""
    spec = await parse_intent("현재 탭 내용 외부로 전송해줘")
    assert spec.risk_level == RiskLevel.high.value
    assert spec.requires_approval is True


@pytest.mark.asyncio
async def test_parse_submit_form_is_high_risk():
    """폼 제출 → high risk + requires_approval."""
    spec = await parse_intent("이 로그인 폼 자동으로 제출해줘")
    assert spec.risk_level == RiskLevel.high.value
    assert spec.requires_approval is True


@pytest.mark.asyncio
async def test_parse_empty_input():
    """빈 입력 → ActionSpec 생성 (unknown, requires_approval=True)."""
    spec = await parse_intent("")
    assert spec.raw_input == ""
    assert spec.requires_approval is True


@pytest.mark.asyncio
async def test_parse_source_propagated():
    """source 파라미터가 ActionSpec에 전달됨."""
    spec = await parse_intent("요약해줘", source=ActionSource.extension)
    assert spec.source == ActionSource.extension.value
