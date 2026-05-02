"""
contracts.py — Vian Brain Kernel SDK Contract (SPEC v1.1)
GENIUS_BRAIN_CONNECTION_SPEC.md 기준 전체 필드 정의.

이 파일은 Brain Kernel의 공식 계약(SDK Contract) 레이어입니다.
외부 코드는 이 모델만 통해 Brain Kernel과 통신합니다.

흐름:
    BrainRequest → VianBrainKernel.process() → BrainResult
    BrainHealth  → health.get_health()
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _uuid() -> str:
    return str(uuid.uuid4())


class BrainRequest(BaseModel):
    """
    Brain Kernel에 전달하는 요청 계약.

    SPEC 필드: request_id, input_text, input_surface, context,
               user_intent_hint, risk_hint, memory_scope,
               commandos_enabled, allow_llm, created_at
    """

    request_id: str = Field(default_factory=_uuid)
    input_text: str                               # 필수 — 사용자 원문 입력
    input_surface: str = "kernel"                 # 입력 출처 (companion_room / hud / api)
    context: Dict[str, Any] = Field(default_factory=dict)
    user_intent_hint: Optional[str] = None        # 상위 레이어 의도 힌트
    risk_hint: Optional[str] = None               # 상위 레이어 위험도 힌트
    memory_scope: str = "session"                 # session / long_term / none
    commandos_enabled: bool = False               # CommandOS 실행 허용 여부
    allow_llm: bool = False                       # Ollama 호출 허용 여부 (WO-003)
    created_at: str = Field(default_factory=_now_iso)

    model_config = {"frozen": False}


class BrainResult(BaseModel):
    """
    Brain Kernel이 반환하는 결과 계약.

    SPEC 필드: request_id, intent_class, risk_class, confidence_score,
               consistency_score, memory_citation, llm_used,
               llm_candidate_response, brain_final_response,
               guard_required, approval_required, allowed_actions,
               blocked_reason, lesson_candidate, pattern_candidate,
               brain_mode, fallback_reason, created_at
    """

    request_id: str
    intent_class: str = "unknown"                 # 비어있으면 안 됨
    risk_class: str = "low"                       # 비어있으면 안 됨
    confidence_score: float = 0.0                 # 0.0~1.0
    consistency_score: float = 0.0               # 0.0~1.0
    memory_citation: Optional[str] = None
    llm_used: bool = False
    llm_candidate_response: Optional[str] = None
    brain_final_response: Optional[str] = None
    guard_required: bool = False
    approval_required: bool = False
    allowed_actions: List[str] = Field(default_factory=list)
    blocked_reason: Optional[str] = None
    lesson_candidate: Optional[str] = None
    pattern_candidate: Optional[str] = None
    brain_mode: str = "kernel"                    # kernel / fallback / degraded
    fallback_reason: Optional[str] = None
    created_at: str = Field(default_factory=_now_iso)

    model_config = {"frozen": False}


class BrainHealth(BaseModel):
    """
    Brain Kernel 상태 헬스 계약.

    SPEC 필드: brain_connected, brain_mode, kernel_version,
               engines_loaded, last_successful_brain_call_at, fallback_reason

    정상 상태: brain_connected=True, brain_mode='kernel', fallback_reason=None
    """

    brain_connected: bool
    brain_mode: str                               # kernel / fallback / degraded
    kernel_version: str
    engines_loaded: List[str] = Field(default_factory=list)
    last_successful_brain_call_at: Optional[str] = None
    fallback_reason: Optional[str] = None

    model_config = {"frozen": False}
