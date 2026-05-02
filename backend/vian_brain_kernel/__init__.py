"""
vian_brain_kernel — Vian Brain Kernel SDK
Brain Kernel의 공식 계약 레이어.

사용:
    from backend.vian_brain_kernel import kernel_version
    from backend.vian_brain_kernel.contracts import BrainRequest, BrainResult, BrainHealth
    from backend.vian_brain_kernel.health import get_health
"""
from __future__ import annotations

kernel_version: str = "1.0.0"

from .contracts import BrainRequest, BrainResult, BrainHealth
from .health import get_health

__all__ = [
    "kernel_version",
    "BrainRequest",
    "BrainResult",
    "BrainHealth",
    "get_health",
]
