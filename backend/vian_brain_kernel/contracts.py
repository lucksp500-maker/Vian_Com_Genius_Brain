"""
contracts.py — Vian Brain Kernel SDK Contract
BrainRequest, BrainResult, BrainHealth Pydantic 모델 정의.

이 파일은 Brain Kernel의 공식 계약(SDK Contract) 레이어입니다.
외부 코드는 이 모델만 통해 Brain Kernel과 통신합니다.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _uuid() -> str:
    return str(uuid.uuid4())


class BrainRequest(BaseModel):
    """Brain Kernel에 전달하는 요청 계약."""

    request_id: str = Field(default_factory=_uuid)
    raw_input: str  # 필수 필드 — 처리할 원시 입력
    source: str = "kernel"
    created_at: datetime = Field(default_factory=_now)

    model_config = {"frozen": False}


class BrainResult(BaseModel):
    """Brain Kernel이 반환하는 결과 계약."""

    request_id: str
    success: bool
    output: Optional[str] = None
    error: Optional[str] = None
    kernel_version: str

    model_config = {"frozen": False}


class BrainHealth(BaseModel):
    """Brain Kernel 상태 헬스 계약."""

    status: str  # "ok" | "degraded" | "down"
    kernel_version: str
    checked_at: datetime = Field(default_factory=_now)

    model_config = {"frozen": False}
