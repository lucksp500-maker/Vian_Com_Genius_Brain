"""
ollama_adapter.py — Ollama Role Lock Adapter (WO-003)
Ollama를 llm_candidate_response 전용 언어 근육으로만 사용합니다.

Role Lock 원칙 (GENIUS_BRAIN_CONNECTION_SPEC.md 기준):
    1. OllamaResult.llm_candidate_response 만 설정
    2. brain_final_response 는 이 어댑터에서 절대 설정 금지
    3. allow_llm=False 이면 HTTP 요청 없이 즉시 None 반환
    4. Ollama 장애 시 예외 propagate 금지 — OllamaResult(None) 반환
    5. 충돌 우선순위: Ground Truth > Guard > 4-Brain > Pattern Memory > Ollama 후보

충돌 해소 책임은 VianBrainKernel (kernel.py) 에 있음. 이 어댑터는 후보만 제공.

[주의] 금지: brain_final_response 설정 / 이유: Ollama는 최종 판단자 아님
[임시] HTTP 호출 방식: sync httpx.Client / WO-004+에서 async 전환 검토 예정
[의존성] 연결: VianBrainKernel.process() — WO-004+에서 연결
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Optional

import httpx

from backend.vian_brain_kernel.contracts import BrainRequest

logger = logging.getLogger(__name__)

_DEFAULT_HOST = "http://localhost:11434"
_DEFAULT_MODEL = "qwen2.5:1.5b"
_DEFAULT_TIMEOUT = 10.0  # seconds


@dataclass
class OllamaResult:
    """
    Ollama 응답 컨테이너.

    Role Lock: llm_candidate_response만 있음.
    brain_final_response 필드 없음 — 구조적으로 최종 응답 불가.
    """

    llm_candidate_response: Optional[str] = None
    llm_used: bool = False


class OllamaAdapter:
    """
    Ollama HTTP API 어댑터.

    Ollama는 언어 근육이다.
    이 어댑터가 반환하는 OllamaResult는 BrainResult.llm_candidate_response에만 들어간다.
    최종 판단(brain_final_response)은 VianBrainKernel이 결정한다.
    """

    def __init__(
        self,
        host: str = _DEFAULT_HOST,
        model: str = _DEFAULT_MODEL,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._host = host.rstrip("/")
        self._model = model
        self._timeout = timeout

    def generate(self, req: BrainRequest, prompt: str) -> OllamaResult:
        """
        Ollama /api/generate 호출.

        Role Lock 강제:
        - allow_llm=False → HTTP 요청 없이 OllamaResult(None) 반환
        - 성공 → OllamaResult(llm_candidate_response=text, llm_used=True)
        - 실패 → OllamaResult(None, False) — 예외 propagate 금지
        """
        # [보호] Role Lock 게이트: allow_llm=False면 Ollama 호출 없음
        if not req.allow_llm:
            return OllamaResult()

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
        }

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(
                    f"{self._host}/api/generate",
                    content=json.dumps(payload).encode(),
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()

            text = data.get("response", "").strip()
            return OllamaResult(
                llm_candidate_response=text or None,
                llm_used=True,
            )

        except Exception as exc:
            logger.warning("OllamaAdapter.generate failed: %s", exc)
            return OllamaResult()
