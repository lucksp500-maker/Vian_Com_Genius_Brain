"""
test_kernel_process.py — WO-002 완료 조건 검증
VianBrainKernel.process() 통합 3케이스 + 엔진 단독 4케이스 + 예외 fallback 1케이스.
"""
from __future__ import annotations

import datetime
from unittest.mock import patch

import pytest

from backend.vian_brain_kernel.contracts import BrainRequest, BrainResult
from backend.vian_brain_kernel.kernel import VianBrainKernel
from backend.vian_brain_kernel.engines.decision_consistency import DecisionConsistencyEngine
from backend.vian_brain_kernel.engines.self_reference_memory import SelfReferenceMemoryEngine
from backend.vian_brain_kernel.engines.internal_confidence import InternalConfidenceEngine
from backend.vian_brain_kernel.engines.pattern_abstraction import PatternAbstractionEngine


def _make_request(**kwargs) -> BrainRequest:
    defaults = {
        "request_id": "test-001",
        "input_text": "제니스 안녕",
        "input_surface": "companion_room",
        "context": {},
        "memory_scope": "session",
        "commandos_enabled": False,
        "allow_llm": False,
        "created_at": datetime.datetime.utcnow().isoformat(),
    }
    defaults.update(kwargs)
    return BrainRequest(**defaults)


# ── 통합 케이스 1: BrainResult 타입 + brain_mode 확인 ────────────────────────
def test_process_returns_brain_result():
    kernel = VianBrainKernel()
    req = _make_request()
    result = kernel.process(req)
    assert isinstance(result, BrainResult)
    assert result.request_id == "test-001"


# ── 통합 케이스 2: brain_mode = 'kernel' ─────────────────────────────────────
def test_process_brain_mode_is_kernel():
    kernel = VianBrainKernel()
    result = kernel.process(_make_request())
    assert result.brain_mode == "kernel"


# ── 통합 케이스 3: 4개 필수 필드 비어있지 않음 ────────────────────────────────
def test_process_required_fields_not_empty():
    kernel = VianBrainKernel()
    result = kernel.process(_make_request(input_text="제니스 안녕"))
    # 인사말 → intent_class = 'greeting'
    assert result.intent_class != ""
    assert result.risk_class != ""
    assert result.confidence_score >= 0.0
    assert result.consistency_score >= 0.0


# ── 엔진 단독 케이스 4: DecisionConsistencyEngine ────────────────────────────
def test_decision_consistency_engine_unit():
    engine = DecisionConsistencyEngine()
    req = _make_request(input_text="어제 받은 견적서 찾아줘")
    result = engine.run(req)
    assert result.intent_class == "search"
    assert result.consistency_score > 0.0


# ── 엔진 단독 케이스 5: SelfReferenceMemoryEngine ────────────────────────────
def test_self_reference_memory_engine_unit():
    engine = SelfReferenceMemoryEngine()
    req = _make_request(input_text="반복 입력 테스트")
    result1 = engine.run(req)
    # 첫 호출 → citation 없음
    assert result1.memory_citation is None
    result2 = engine.run(req)
    # 두 번째 동일 입력 → citation 생성
    assert result2.memory_citation is not None
    assert "prior:" in result2.memory_citation


# ── 엔진 단독 케이스 6: InternalConfidenceEngine ─────────────────────────────
def test_internal_confidence_engine_unit():
    engine = InternalConfidenceEngine()
    # 위험 입력
    high_req = _make_request(input_text="파일 삭제해줘")
    high_result = engine.run(high_req)
    assert high_result.risk_class == "high"
    assert high_result.approval_required is True
    # 일반 입력
    low_req = _make_request(input_text="제니스 안녕")
    low_result = engine.run(low_req)
    assert low_result.risk_class == "low"
    assert low_result.confidence_score >= 0.5


# ── 엔진 단독 케이스 7: PatternAbstractionEngine ─────────────────────────────
def test_pattern_abstraction_engine_unit():
    engine = PatternAbstractionEngine()
    req = _make_request(input_text="패턴 테스트 반복 입력_unique_xyz")
    # 3회 미만 → candidate 없음
    for _ in range(2):
        result = engine.run(req)
    assert result.pattern_candidate is None
    # 3회 → candidate 생성
    result3 = engine.run(req)
    assert result3.pattern_candidate is not None
    assert "rule_candidate:" in result3.pattern_candidate


# ── fallback 케이스 8: 엔진 예외 시 process() 계속 실행 ─────────────────────
def test_engine_exception_fallback_continues():
    kernel = VianBrainKernel()
    req = _make_request()

    # DecisionConsistencyEngine이 예외를 던지도록 패치
    with patch.object(kernel._consistency, "run", side_effect=RuntimeError("엔진 강제 오류")):
        result = kernel.process(req)

    # 예외에도 불구하고 BrainResult가 반환됨
    assert isinstance(result, BrainResult)
    assert result.brain_mode == "kernel"
    # fallback 기본값 확인
    assert result.intent_class == "unknown"
    assert result.consistency_score == 0.0
