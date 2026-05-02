"""
self_reference_memory.py — Self-Reference Memory Engine (WO-002)
이전 판단/승인/실패 기록을 현재 판단 근거로 인용하는 엔진.
WO-002: 세션 내 인메모리 저장. SQLite 연결은 WO-004+.

흐름:
    BrainRequest.request_id + memory_scope
        → 세션 캐시 조회
        → memory_citation 생성
        → MemoryResult
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional

from backend.vian_brain_kernel.contracts import BrainRequest

# [임시] 세션 내 인메모리 캐시 — WO-004에서 SQLite로 교체
_session_cache: Dict[str, str] = {}


@dataclass
class MemoryResult:
    memory_citation: Optional[str] = None
    lesson_candidate: Optional[str] = None


class SelfReferenceMemoryEngine:
    """
    세션 내 이전 판단을 인용합니다.

    WO-002: 인메모리 캐시만. 세션 간 지속성 없음.
    WO-004+에서 parenting_events.jsonl / SQLite 연동으로 교체.
    """

    def run(self, req: BrainRequest) -> MemoryResult:
        if req.memory_scope == "none":
            return MemoryResult()

        key = f"{req.input_surface}:{req.input_text[:40]}"
        prior = _session_cache.get(key)

        citation = None
        lesson = None
        if prior:
            citation = f"prior:{prior}"
            lesson = f"repeated_input:{req.input_text[:20]}"

        # 현재 요청을 캐시에 저장 (다음 동일 입력 시 인용)
        _session_cache[key] = req.request_id

        return MemoryResult(
            memory_citation=citation,
            lesson_candidate=lesson,
        )
