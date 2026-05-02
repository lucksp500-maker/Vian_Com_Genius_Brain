"""
ActionSpec — Vian CommandOS × Genius Brain Nursery V2.0
자연어/기계어/브라우저/파일 명령을 하나의 구조화된 스키마로 통합합니다.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class ActionSource(str, Enum):
    hud = "hud"
    extension = "extension"
    api = "api"
    direct = "direct"


class TargetType(str, Enum):
    file = "file"
    url = "url"
    browser_tab = "browser_tab"
    text = "text"
    system = "system"
    unknown = "unknown"


class RiskLevel(str, Enum):
    none = "none"
    low = "low"
    medium = "medium"
    high = "high"


class GuardResult(str, Enum):
    allow = "allow"
    deny = "deny"
    ask = "ask"


class ExecutionState(str, Enum):
    pending = "pending"
    guard_approved = "guard_approved"
    user_approved = "user_approved"
    user_rejected = "user_rejected"
    executed = "executed"
    failed = "failed"
    stopped = "stopped"


class ActionSpec(BaseModel):
    """
    모든 Vian CommandOS 명령의 통합 스키마.

    흐름:
    raw_input → AI Intent Bridge → ActionSpec (pending)
                                        ↓
                                  Guard Policy Gate
                                        ↓
                              Action Preview (user sees this)
                                        ↓
                                  User Approve/Reject
                                        ↓
                                  Execution Kernel
    """
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: ActionSource = ActionSource.hud
    raw_input: str
    intent: str = ""
    target_type: TargetType = TargetType.unknown
    target_ref: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.none
    requires_approval: bool = False
    preview_required: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    guard_result: Optional[GuardResult] = None
    guard_reason: Optional[str] = None
    execution_state: ExecutionState = ExecutionState.pending
    confidence_score: Optional[float] = None

    model_config = {"use_enum_values": True}


class ActionSpecCreateRequest(BaseModel):
    raw_input: str
    source: ActionSource = ActionSource.hud


class ActionSpecResponse(BaseModel):
    action_id: str
    intent: str
    target_type: str
    risk_level: str
    requires_approval: bool
    guard_result: Optional[str]
    guard_reason: Optional[str]
    execution_state: str
    confidence_score: Optional[float]
    preview_url: Optional[str] = None


def make_preview_url(action_id: str, base_url: str = "http://localhost:5051") -> str:
    return f"{base_url}/command-room/preview/{action_id}"
