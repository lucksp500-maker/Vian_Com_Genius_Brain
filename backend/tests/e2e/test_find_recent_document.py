"""
E2E 테스트: "어제 받은 견적서 찾아줘" — WO-008

검증 흐름:
    자연어 입력 → AI Intent Bridge → ActionSpec(target_type=file)
    → Local Indexer 검색 → 결과 반환

완료 조건:
    - intent가 '파일 검색' 또는 'search' 의미를 포함
    - target_type = 'file' (브라우저/시스템 아님)
    - Local Index 검색 결과 반환 (결과 없어도 빈 배열로 정상 응답)
    - Guard 결과 allow 또는 ask (deny 아님)
"""
import pytest

from backend.core.commandos.ai_intent_bridge import parse_intent
from backend.core.commandos.action_spec import TargetType, GuardResult
from backend.core.guard.policy_engine import evaluate
from backend.core.indexer.local_indexer import LocalIndexer


@pytest.mark.asyncio
async def test_find_recent_document_intent_classification():
    """
    "어제 받은 견적서 찾아줘" → intent_class = file search 분류 검증.
    AI Intent Bridge가 '파일 검색'으로 올바르게 분류하는지 확인합니다.
    """
    spec = await parse_intent(raw_input="어제 받은 견적서 찾아줘", source="hud")

    # target_type: file 이어야 함
    assert spec.target_type == TargetType.file.value, (
        f"WO-008 E2E 실패: '견적서 찾아줘' → target_type=file 예상, "
        f"실제: {spec.target_type}"
    )


@pytest.mark.asyncio
async def test_find_recent_document_guard_not_deny():
    """
    파일 검색 명령은 Guard에서 deny되지 않습니다 (allow 또는 ask).
    """
    spec = await parse_intent(raw_input="어제 받은 견적서 찾아줘", source="hud")
    evaluation = evaluate(spec)

    assert evaluation.result.value != GuardResult.deny.value, (
        f"WO-008 E2E 실패: 파일 검색 명령이 Guard에서 deny됨. "
        f"reason: {evaluation.reason}"
    )


@pytest.mark.asyncio
async def test_find_recent_document_local_index_responds():
    """
    Local Indexer가 '견적서' 검색어에 대해 정상 응답합니다.
    결과가 없어도 빈 리스트 + 예외 없음이 성공 조건입니다.
    """
    indexer = LocalIndexer()
    results = await indexer.search("견적서")

    # 예외 없이 리스트 반환 — 결과 0개도 정상
    assert isinstance(results, list), (
        "WO-008 E2E 실패: Local Indexer가 리스트를 반환하지 않음"
    )


@pytest.mark.asyncio
async def test_find_recent_document_full_pipeline():
    """
    완전 파이프라인: 자연어 → ActionSpec → Guard → Indexer 검색.
    3단계 모두 정상 완료해야 합니다.
    """
    # 1단계: Intent 파싱
    spec = await parse_intent(raw_input="어제 받은 견적서 찾아줘", source="hud")
    assert spec.action_id

    # 2단계: Guard 평가
    evaluation = evaluate(spec)
    assert evaluation.result.value in ("allow", "ask"), (
        f"Guard deny: {evaluation.reason}"
    )

    # 3단계: Local Index 검색
    indexer = LocalIndexer()
    results = await indexer.search("견적서")
    assert isinstance(results, list)
