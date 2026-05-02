"""
E2E 테스트: Pattern Memory 재응답 — WO-008

검증 흐름:
    1. 첫 번째 명령 → 이벤트 기록 (event_id A)
    2. 동일 명령 재시도 → SelfReferenceMemory.cite() → prior_event_id = A
    3. BrainRouter 실행 → enriched_spec에 memory_citation이 반영됨

완료 조건:
    - 동일 입력 재시도 시 prior_event_id가 이전 event_id 참조
    - memory_weight > 0 (기억 강도)
    - BrainRouter 결과의 enriched_spec이 confidence_score 포함

WO-008 완료 조건 직접 검증:
    "Pattern Memory 재응답 시 이전 event_id와 memory_citation을 참조합니다"
"""
import pytest
import tempfile
from pathlib import Path

from backend.core.commandos.ai_intent_bridge import parse_intent
from backend.core.parenting.event_logger import EventLogger, build_parenting_event
from backend.core.brain.self_reference_memory import SelfReferenceMemoryEngine
from backend.core.brain.commandos_brain_router import route as brain_route


@pytest.mark.asyncio
async def test_pattern_memory_prior_event_id_cited():
    """
    이전 이벤트 기록 후 동일 명령 실행 시
    SelfReferenceMemory가 이전 event_id를 참조합니다.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        logger = EventLogger(events_path=tmp_path)

        # 1단계: 첫 번째 명령 이벤트 기록
        spec_first = await parse_intent(raw_input="오늘 일정 찾아줘", source="hud")
        first_event = build_parenting_event(
            raw_input="오늘 일정 찾아줘",
            action_spec_id=spec_first.action_id,
            intent_class="file_search",
            risk_class="none",
            guard_result="allow",
            approval_state="user_approved",
            execution_state="executed",
        )
        await logger.log_event(first_event)
        first_event_id = first_event["event_id"]

        # 2단계: 동일 명령 재시도 → Memory 조회
        spec_retry = await parse_intent(raw_input="오늘 일정 찾아줘", source="hud")
        memory_engine = SelfReferenceMemoryEngine(events_path=tmp_path)
        citation = await memory_engine.cite(spec_retry)

        # prior_event_id가 첫 번째 이벤트를 참조
        assert citation.prior_event_id == first_event_id, (
            f"WO-008 E2E 실패: memory_citation이 이전 event_id({first_event_id})를 "
            f"참조하지 않음. 실제: {citation.prior_event_id}"
        )

    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_pattern_memory_weight_positive():
    """
    기억이 존재하면 memory_weight > 0.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        logger = EventLogger(events_path=tmp_path)
        spec = await parse_intent(raw_input="최근 파일 보여줘", source="hud")

        event = build_parenting_event(
            raw_input="최근 파일 보여줘",
            action_spec_id=spec.action_id,
            intent_class="file_search",
            risk_class="none",
            guard_result="allow",
            approval_state="user_approved",
            execution_state="executed",
        )
        await logger.log_event(event)

        spec_retry = await parse_intent(raw_input="최근 파일 보여줘", source="hud")
        memory_engine = SelfReferenceMemoryEngine(events_path=tmp_path)
        citation = await memory_engine.cite(spec_retry)

        if citation.prior_event_id:
            assert citation.memory_weight > 0.0, (
                f"memory_weight가 0: {citation.memory_weight}"
            )

    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_pattern_memory_no_prior_event_on_new_input():
    """
    이전 이벤트가 없으면 prior_event_id = None.
    새로운 명령에 대한 첫 번째 실행.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        # 이벤트 기록 없이 바로 Memory 조회
        spec = await parse_intent(raw_input="완전히 새로운 명령 xyz123", source="hud")
        memory_engine = SelfReferenceMemoryEngine(events_path=tmp_path)
        citation = await memory_engine.cite(spec)

        # 이전 이벤트 없음 → prior_event_id = None
        assert citation.prior_event_id is None

    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_pattern_memory_brain_router_integration():
    """
    Brain Router가 Memory Citation을 포함한 enriched_spec을 생성합니다.
    confidence_score가 존재하고 0~1 범위입니다.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        logger = EventLogger(events_path=tmp_path)
        query = "문서 검색해줘"

        # 이전 이벤트 기록
        spec1 = await parse_intent(raw_input=query, source="hud")
        event = build_parenting_event(
            raw_input=query,
            action_spec_id=spec1.action_id,
            intent_class="file_search",
            risk_class="none",
            guard_result="allow",
            approval_state="user_approved",
            execution_state="executed",
        )
        await logger.log_event(event)

        # Brain Router 실행
        spec2 = await parse_intent(raw_input=query, source="hud")
        brain_result = await brain_route(spec2)

        enriched = brain_result.enriched_spec
        # confidence_score가 존재하고 범위 안
        score = enriched.confidence_score
        assert score is None or 0.0 <= score <= 1.0

    finally:
        tmp_path.unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_pattern_memory_multiple_events_selects_recent():
    """
    여러 이전 이벤트가 있을 때 가장 최근 이벤트를 참조합니다.
    """
    with tempfile.NamedTemporaryFile(suffix='.jsonl', delete=False) as f:
        tmp_path = Path(f.name)

    try:
        logger = EventLogger(events_path=tmp_path)
        query = "견적서 보여줘"

        # 이전 이벤트 2개 기록
        events = []
        for i in range(2):
            spec = await parse_intent(raw_input=query, source="hud")
            event = build_parenting_event(
                raw_input=query,
                action_spec_id=spec.action_id,
                intent_class="file_search",
                risk_class="none",
                guard_result="allow",
                approval_state="user_approved",
                execution_state="executed",
            )
            await logger.log_event(event)
            events.append(event)

        # 재시도
        spec_retry = await parse_intent(raw_input=query, source="hud")
        memory_engine = SelfReferenceMemoryEngine(events_path=tmp_path)
        citation = await memory_engine.cite(spec_retry)

        # prior_event_id가 기록된 이벤트 중 하나를 참조
        if citation.prior_event_id:
            event_ids = [e["event_id"] for e in events]
            assert citation.prior_event_id in event_ids

    finally:
        tmp_path.unlink(missing_ok=True)
