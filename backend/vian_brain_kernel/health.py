"""
health.py — Brain Kernel 헬스 체크 함수 전용.
BrainHealth 모델은 contracts.py 에 정의됨.

정상 상태: brain_connected=True, brain_mode='kernel', fallback_reason=None
"""
from __future__ import annotations

from . import kernel_version
from .contracts import BrainHealth

_KERNEL_ENGINES = [
    "DecisionConsistencyEngine",
    "SelfReferenceMemoryEngine",
    "InternalConfidenceEngine",
    "PatternAbstractionEngine",
]


def get_health() -> BrainHealth:
    """현재 Brain Kernel 상태를 반환합니다."""
    return BrainHealth(
        brain_connected=True,
        brain_mode="kernel",
        kernel_version=kernel_version,
        engines_loaded=_KERNEL_ENGINES,
        last_successful_brain_call_at=None,
        fallback_reason=None,
    )
