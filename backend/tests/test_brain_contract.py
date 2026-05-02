"""
test_brain_contract.py — WO-001 계약 검증 (SPEC v1.1 기준 업데이트)
BrainRequest, BrainResult, BrainHealth 모델 + kernel_version + 직렬화 6케이스.
"""
from __future__ import annotations

import pytest
from pydantic import ValidationError

from backend.vian_brain_kernel import kernel_version
from backend.vian_brain_kernel.contracts import BrainHealth, BrainRequest, BrainResult
from backend.vian_brain_kernel.health import get_health


# ── 케이스 1: BrainRequest 정상 생성 + 직렬화 ────────────────────────────────
def test_brain_request_create_and_serialize():
    req = BrainRequest(input_text="이 PDF 요약해줘")
    assert req.input_text == "이 PDF 요약해줘"
    assert req.request_id
    assert req.memory_scope == "session"
    assert req.allow_llm is False
    data = req.model_dump()
    assert data["input_text"] == "이 PDF 요약해줘"
    json_str = req.model_dump_json()
    assert "이 PDF 요약해줘" in json_str


# ── 케이스 2: BrainResult JSON 역직렬화 roundtrip ────────────────────────────
def test_brain_result_json_roundtrip():
    result = BrainResult(
        request_id="test-id-001",
        intent_class="summarize",
        risk_class="low",
        confidence_score=0.85,
        consistency_score=0.8,
        brain_mode="kernel",
    )
    json_str = result.model_dump_json()
    restored = BrainResult.model_validate_json(json_str)
    assert restored.request_id == "test-id-001"
    assert restored.intent_class == "summarize"
    assert restored.brain_mode == "kernel"
    assert restored.confidence_score == pytest.approx(0.85)


# ── 케이스 3: BrainHealth 정상 생성 ──────────────────────────────────────────
def test_brain_health_create():
    health = BrainHealth(
        brain_connected=True,
        brain_mode="kernel",
        kernel_version=kernel_version,
        engines_loaded=["DecisionConsistencyEngine"],
    )
    assert health.brain_connected is True
    assert health.brain_mode == "kernel"
    assert health.fallback_reason is None


# ── 케이스 4: kernel_version 반환 확인 ───────────────────────────────────────
def test_kernel_version_returned():
    assert isinstance(kernel_version, str)
    assert kernel_version
    parts = kernel_version.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


# ── 케이스 5: get_health() 정상 상태 + 엔진 목록 확인 ────────────────────────
def test_get_health_kernel_version_matches():
    health = get_health()
    assert isinstance(health, BrainHealth)
    assert health.brain_connected is True
    assert health.brain_mode == "kernel"
    assert health.kernel_version == kernel_version
    assert len(health.engines_loaded) == 4
    assert health.fallback_reason is None


# ── 케이스 6: BrainRequest 필수 필드 누락 시 ValidationError ─────────────────
def test_brain_request_missing_field_raises():
    with pytest.raises(ValidationError):
        BrainRequest()  # input_text 누락
