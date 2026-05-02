"""
test_brain_contract.py — WO-001 완료 조건 검증
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
    req = BrainRequest(raw_input="이 PDF 요약해줘")
    assert req.raw_input == "이 PDF 요약해줘"
    assert req.request_id  # uuid 생성됨
    data = req.model_dump()
    assert data["raw_input"] == "이 PDF 요약해줘"
    json_str = req.model_dump_json()
    assert "이 PDF 요약해줘" in json_str


# ── 케이스 2: BrainResult JSON 역직렬화 roundtrip ────────────────────────────
def test_brain_result_json_roundtrip():
    result = BrainResult(
        request_id="test-id-001",
        success=True,
        output="요약 완료",
        kernel_version=kernel_version,
    )
    json_str = result.model_dump_json()
    restored = BrainResult.model_validate_json(json_str)
    assert restored.request_id == "test-id-001"
    assert restored.success is True
    assert restored.output == "요약 완료"
    assert restored.kernel_version == kernel_version


# ── 케이스 3: BrainHealth 정상 생성 ──────────────────────────────────────────
def test_brain_health_create():
    health = BrainHealth(status="ok", kernel_version=kernel_version)
    assert health.status == "ok"
    assert health.kernel_version == kernel_version
    assert health.checked_at is not None


# ── 케이스 4: kernel_version 반환 확인 ───────────────────────────────────────
def test_kernel_version_returned():
    assert isinstance(kernel_version, str)
    assert kernel_version  # 빈 문자열 아님
    # semver 형식 최소 검증: 숫자.숫자.숫자
    parts = kernel_version.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)


# ── 케이스 5: get_health() kernel_version 일치 ───────────────────────────────
def test_get_health_kernel_version_matches():
    health = get_health()
    assert isinstance(health, BrainHealth)
    assert health.status == "ok"
    assert health.kernel_version == kernel_version


# ── 케이스 6: BrainRequest 필수 필드 누락 시 ValidationError ─────────────────
def test_brain_request_missing_field_raises():
    with pytest.raises(ValidationError):
        BrainRequest()  # raw_input 누락
