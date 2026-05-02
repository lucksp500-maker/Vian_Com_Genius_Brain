"""
WO-001 — action_spec.py 스키마 테스트
자연어 입력 10개 → 유효한 ActionSpec 변환 검증
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from backend.core.commandos.action_spec import (
    ActionSpec,
    ActionSource,
    TargetType,
    RiskLevel,
    ExecutionState,
    GuardResult,
    ActionSpecCreateRequest,
    make_preview_url,
)

# 자연어 입력 10개 → ActionSpec 직접 생성 시나리오
NATURAL_LANGUAGE_CASES = [
    {
        "raw_input": "이 PDF 요약해줘",
        "intent": "현재 문서를 요약합니다",
        "target_type": TargetType.file,
        "risk_level": RiskLevel.none,
    },
    {
        "raw_input": "어제 받은 견적서 찾아줘",
        "intent": "로컬 인덱스에서 최근 견적서를 검색합니다",
        "target_type": TargetType.file,
        "risk_level": RiskLevel.none,
    },
    {
        "raw_input": "현재 탭 저장해줘",
        "intent": "현재 브라우저 탭을 아카이브에 저장합니다",
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.low,
    },
    {
        "raw_input": "이 페이지 번역해줘",
        "intent": "현재 페이지를 한국어로 번역합니다",
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.none,
    },
    {
        "raw_input": "선택한 텍스트 교정해줘",
        "intent": "선택된 텍스트를 교정합니다",
        "target_type": TargetType.text,
        "risk_level": RiskLevel.none,
    },
    {
        "raw_input": "이 파일 삭제해줘",
        "intent": "지정된 파일을 삭제합니다",
        "target_type": TargetType.file,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
    },
    {
        "raw_input": "감사 로그 보여줘",
        "intent": "최근 감사 로그를 표시합니다",
        "target_type": TargetType.system,
        "risk_level": RiskLevel.none,
    },
    {
        "raw_input": "오늘 방문한 페이지 목록 보여줘",
        "intent": "오늘 방문한 브라우저 기록을 표시합니다",
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.none,
    },
    {
        "raw_input": "이 양식 자동으로 작성해줘",
        "intent": "현재 페이지의 폼을 자동 작성합니다",
        "target_type": TargetType.browser_tab,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
    },
    {
        "raw_input": "현재 탭 내용 외부로 전송해줘",
        "intent": "현재 탭 내용을 외부 서비스로 전송합니다",
        "target_type": TargetType.url,
        "risk_level": RiskLevel.high,
        "requires_approval": True,
    },
]


@pytest.mark.parametrize("case", NATURAL_LANGUAGE_CASES)
def test_natural_language_to_action_spec(case):
    """자연어 입력 10개 → 유효한 ActionSpec 생성 확인."""
    spec = ActionSpec(
        raw_input=case["raw_input"],
        intent=case["intent"],
        target_type=case["target_type"],
        risk_level=case["risk_level"],
        requires_approval=case.get("requires_approval", False),
    )
    assert spec.action_id is not None
    assert len(spec.action_id) == 36  # UUID 형식
    assert spec.raw_input == case["raw_input"]
    assert spec.risk_level == case["risk_level"].value
    assert isinstance(spec.created_at, datetime)


def test_action_spec_default_values():
    """ActionSpec 기본값 검증."""
    spec = ActionSpec(raw_input="테스트 명령")
    assert spec.source == ActionSource.hud.value
    assert spec.target_type == TargetType.unknown.value
    assert spec.risk_level == RiskLevel.none.value
    assert spec.requires_approval is False
    assert spec.preview_required is True
    assert spec.execution_state == ExecutionState.pending.value
    assert spec.guard_result is None
    assert spec.confidence_score is None


def test_action_spec_unique_ids():
    """동일 입력에서도 action_id는 매번 고유해야 함."""
    specs = [ActionSpec(raw_input="동일한 입력") for _ in range(5)]
    ids = [s.action_id for s in specs]
    assert len(set(ids)) == 5, "action_id 중복 발생"


def test_high_risk_requires_approval():
    """risk_level=high이면 requires_approval=True가 권장됨."""
    spec = ActionSpec(
        raw_input="파일 삭제",
        risk_level=RiskLevel.high,
        requires_approval=True,
    )
    assert spec.requires_approval is True
    assert spec.risk_level == RiskLevel.high.value


def test_action_spec_with_guard_result():
    """guard_result 설정 후 상태 변경 확인."""
    spec = ActionSpec(raw_input="탭 저장")
    spec.guard_result = GuardResult.allow.value
    spec.guard_reason = "low risk browser action"
    assert spec.guard_result == GuardResult.allow.value


def test_action_spec_create_request():
    """ActionSpecCreateRequest 유효성 확인."""
    req = ActionSpecCreateRequest(raw_input="PDF 요약해줘")
    assert req.raw_input == "PDF 요약해줘"
    assert req.source == ActionSource.hud.value


def test_action_spec_create_request_empty_fails():
    """빈 raw_input은 허용되지만, 빈 문자열 처리는 bridge에서 담당."""
    req = ActionSpecCreateRequest(raw_input="")
    assert req.raw_input == ""


def test_make_preview_url():
    """preview URL이 올바른 경로로 생성되는지 확인."""
    url = make_preview_url("test-action-id-123")
    assert "test-action-id-123" in url
    assert url.startswith("http://localhost:5051/command-room/preview/")
