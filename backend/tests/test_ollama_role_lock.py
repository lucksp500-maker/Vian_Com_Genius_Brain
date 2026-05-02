"""
test_ollama_role_lock.py — WO-003 완료 조건 검증
OllamaAdapter Role Lock 5케이스 (모두 mock 기반 — 실제 Ollama 서버 불필요).
"""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import httpx
import pytest

from backend.vian_brain_kernel.contracts import BrainRequest
from backend.vian_brain_kernel.adapters.ollama_adapter import OllamaAdapter, OllamaResult


def _make_request(**kwargs) -> BrainRequest:
    defaults = {
        "input_text": "이 PDF 요약해줘",
        "allow_llm": True,
    }
    defaults.update(kwargs)
    return BrainRequest(**defaults)


def _mock_httpx_response(text: str) -> MagicMock:
    """Ollama /api/generate 성공 응답 mock"""
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"response": text}
    mock_resp.raise_for_status.return_value = None
    return mock_resp


# ── 케이스 1: allow_llm=False → HTTP 요청 없음, None 반환 ───────────────────
def test_allow_llm_false_skips_http():
    adapter = OllamaAdapter()
    req = _make_request(allow_llm=False)

    with patch("httpx.Client") as mock_client_cls:
        result = adapter.generate(req, prompt="요약해줘")

    # HTTP 클라이언트 생성 자체가 없어야 함
    mock_client_cls.assert_not_called()
    assert isinstance(result, OllamaResult)
    assert result.llm_candidate_response is None
    assert result.llm_used is False


# ── 케이스 2: Ollama 성공 → llm_candidate_response 설정, llm_used=True ───────
def test_ollama_success_returns_candidate():
    adapter = OllamaAdapter()
    req = _make_request(allow_llm=True)
    expected_text = "이 문서는 2024년 3분기 실적 보고서입니다."

    mock_resp = _mock_httpx_response(expected_text)
    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.return_value = mock_resp

    with patch("httpx.Client", return_value=mock_client):
        result = adapter.generate(req, prompt="요약해줘")

    assert isinstance(result, OllamaResult)
    assert result.llm_candidate_response == expected_text
    assert result.llm_used is True


# ── 케이스 3: Ollama ConnectError → None 반환, 예외 propagate 없음 ──────────
def test_ollama_connection_error_graceful():
    adapter = OllamaAdapter()
    req = _make_request(allow_llm=True)

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.side_effect = httpx.ConnectError("연결 실패")

    with patch("httpx.Client", return_value=mock_client):
        result = adapter.generate(req, prompt="요약해줘")

    assert isinstance(result, OllamaResult)
    assert result.llm_candidate_response is None
    assert result.llm_used is False


# ── 케이스 4: Ollama TimeoutException → None 반환 ────────────────────────────
def test_ollama_timeout_graceful():
    adapter = OllamaAdapter()
    req = _make_request(allow_llm=True)

    mock_client = MagicMock()
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_client.post.side_effect = httpx.TimeoutException("타임아웃")

    with patch("httpx.Client", return_value=mock_client):
        result = adapter.generate(req, prompt="요약해줘")

    assert isinstance(result, OllamaResult)
    assert result.llm_candidate_response is None
    assert result.llm_used is False


# ── 케이스 5: Role Lock 구조 검증 — brain_final_response 필드 없음 ───────────
def test_role_lock_no_brain_final_field():
    """
    OllamaResult에 brain_final_response 속성이 없음을 검증.
    구조적으로 Ollama가 최종 응답을 낼 수 없도록 강제.
    """
    result = OllamaResult(llm_candidate_response="후보 응답", llm_used=True)
    assert not hasattr(result, "brain_final_response"), (
        "Role Lock 위반: OllamaResult에 brain_final_response 필드가 있으면 안 됩니다"
    )
    assert hasattr(result, "llm_candidate_response")
    assert hasattr(result, "llm_used")
