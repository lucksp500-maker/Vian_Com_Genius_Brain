"""
health.py — Brain Kernel 헬스 체크 함수 전용.
BrainHealth 모델은 contracts.py 에 정의됨.
"""
from __future__ import annotations

from .contracts import BrainHealth
from . import kernel_version


def get_health() -> BrainHealth:
    """현재 Brain Kernel 상태를 반환합니다."""
    return BrainHealth(
        status="ok",
        kernel_version=kernel_version,
    )
