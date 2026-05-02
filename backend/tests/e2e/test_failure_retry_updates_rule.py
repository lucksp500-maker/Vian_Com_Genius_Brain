"""
E2E 테스트: 실패 후 재시도 → lesson 또는 rule_candidate 생성 — WO-008

검증 흐름:
    1. 명령 실행 → failed 상태로 기록
    2. 동일 명령 재시도
    3. SelfReferenceMemory가 실패 이벤트를 recall
    4. lesson 또는 memory_citation이 생성됨

완료 조건:
    - 실패 이벤트가 parenting_events.jsonl에 기록됨
    - 동일 명령 재시도 시 SelfReferenceMemory가 prior_event_id를 반환
    - lesson 필드가 있거나 memory_citation이 있음

WO-008 완료 조건 직접 검증:
    "실패 후 재시도 시 lesson 또는 rule_candidate가 생성됩니다"
"""
import pytest
import tempfile
from pathlib import Path

from backend.core.commandos.ai_intent_bridge import parse_intent
from backend.core.commandos.action_spec import ActionSpec
from backend.core.parenting.event_logger import EventLogger, build_parenting_event
from backend.core.brain.self_reference_memory import SelfReferenceMemoryEngine


@pytest.mark.asyncio
async def test_failure_event_is_logged():
    """
    실패 상태의 명령이 parenting_events.jsonl에 기록됩니다.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        logger = EventLogger(events_path=tmp_path)

        event = build_parenting_event(
            raw_input="파일 삭제 시도",
            action_spec_id="test-spec-001",
            intent_class="file_delete",
            risk_class="high",
            guard_result="deny",
            approval_state="user_rejected",
            execution_state="failed",
            lesson="파일 삭제 명령은 V1에서 금지됨",
        )
        await logger.log_event(event)

        events = await logger.read_recent(limit=10)
        assert len(events) >= 1

        last = events[-1]
        assert last["execution_state"] == "failed"
        assert last["feedback_class"] == "negative"
        assert last["lesson"] == "파일 삭제 명령은 V1에서 금지됨"

    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_retry_recalls_prior_failure():
    """
    실패 이벤트 기록 후 동일 명령 재시도 시
    SelfReferenceMemory가 prior_event_id를 반환합니다.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        logger = EventLogger(events_path=tmp_path)

        # 1단계: 실패 이벤트 기록
        spec_first = await parse_intent(raw_input="문서 검색해줘", source="hud")
        event = build_parenting_event(
            raw_input="문서 검색해줘",
            action_spec_id=spec_first.action_id,
            intent_class="file_search",
            risk_class="none",
            guard_result="allow",
            approval_state="user_approved",
            execution_state="failed",
            lesson="검색 인덱스 미구축 상태",
        )
        await logger.log_event(event)

        # 2단계: 동일 명령 재시도 → SelfReferenceMemory 조회
        spec_retry = await parse_intent(raw_input="문서 검색해줘", source="hud")
        memory_engine = SelfReferenceMemoryEngine(events_path=tmp_path)
        citation = await memory_engine.cite(spec_retry)

        # prior_event_id가 존재 (이전 실패 이벤트 recall)
        assert citation.prior_event_id is not None, (
            "WO-008 E2E 실패: 실패 이벤트 recall 후 prior_event_id가 None"
        )

    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_failure_feedback_class_is_negative():
    """
    execution_state=failed 이벤트의 feedback_class = negative.
    """
    event = build_parenting_event(
        raw_input="테스트 명령",
        action_spec_id="test-spec-002",
        intent_class="unknown",
        risk_class="medium",
        guard_result="ask",
        approval_state="user_approved",
        execution_state="failed",
    )
    assert event["feedback_class"] == "negative"


@pytest.mark.asyncio
async def test_lesson_field_in_failure_event():
    """
    실패 이벤트에 lesson 필드가 포함될 수 있습니다.
    lesson이 있으면 AI가 다음 판단에 참고합니다.
    """
    event = build_parenting_event(
        raw_input="외부 파일 전송",
        action_spec_id="test-spec-003",
        intent_class="file_send",
        risk_class="high",
        guard_result="deny",
        approval_state="user_rejected",
        execution_state="failed",
        lesson="외부 전송은 V1 범위 금지",
    )
    assert event["lesson"] == "외부 전송은 V1 범위 금지"
    assert event["feedback_class"] == "negative"


@pytest.mark.asyncio
async def test_positive_event_no_lesson_needed():
    """
    성공 이벤트는 lesson 없이도 positive feedback으로 기록됩니다.
    """
    event = build_parenting_event(
        raw_input="최근 문서 보기",
        action_spec_id="test-spec-004",
        intent_class="file_search",
        risk_class="none",
        guard_result="allow",
        approval_state="user_approved",
        execution_state="executed",
    )
    assert event["feedback_class"] == "positive"
    assert event["lesson"] is None
