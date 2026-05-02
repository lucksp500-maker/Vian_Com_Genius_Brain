"""
Guard Policy Engine — WO-002
Vian_CommandOS policy-gate.ts의 Python 포팅.
ActionSpec에 대해 allow / deny / ask 판정을 수행합니다.

[보호] 이유: 실행 차단 로직의 핵심 / 수정 필요 시: 정책 규칙만 수정, PolicyResult 타입 변경 금지
"""
from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel

from backend.core.commandos.action_spec import ActionSpec, RiskLevel, TargetType


class PolicyResult(str, Enum):
    allow = "allow"
    deny = "deny"
    ask = "ask"


class PolicyEvaluation(BaseModel):
    result: PolicyResult
    reason: str
    risk_level: str
    requires_approval: bool
    action_id: str


# 즉시 deny — target_type=unknown이고 confidence 없는 경우
_DENY_TARGET_TYPES = {TargetType.unknown.value}

# 항상 ask — risk_level medium 이상 또는 requires_approval=True
_ASK_RISK_LEVELS = {RiskLevel.high.value, RiskLevel.medium.value}

# 항상 allow — risk_level=none, requires_approval=False
_ALLOW_RISK_LEVELS = {RiskLevel.none.value, RiskLevel.low.value}


def evaluate(spec: ActionSpec) -> PolicyEvaluation:
    """
    ActionSpec에 대해 정책 판정을 수행합니다.

    판정 우선순위:
    1. target_type=unknown AND requires_approval=True → deny
    2. risk_level=high 또는 requires_approval=True → ask
    3. risk_level=medium → ask
    4. risk_level=none 또는 low → allow
    5. 나머지 → deny (안전 우선)
    """
    risk = spec.risk_level
    target = spec.target_type

    # 1순위: unknown + 승인 필요 → deny
    if target in _DENY_TARGET_TYPES and spec.requires_approval:
        return PolicyEvaluation(
            result=PolicyResult.deny,
            reason=f"대상 유형 불명확('{target}') + 승인 필요 — 실행 차단",
            risk_level=risk,
            requires_approval=spec.requires_approval,
            action_id=spec.action_id,
        )

    # 2순위: high risk 또는 requires_approval 명시 → ask
    if risk == RiskLevel.high.value or spec.requires_approval:
        return PolicyEvaluation(
            result=PolicyResult.ask,
            reason=f"위험도 '{risk}' — 사용자 승인 후 실행",
            risk_level=risk,
            requires_approval=True,
            action_id=spec.action_id,
        )

    # 3순위: medium risk → ask
    if risk == RiskLevel.medium.value:
        return PolicyEvaluation(
            result=PolicyResult.ask,
            reason=f"위험도 '{risk}' — 확인 후 실행",
            risk_level=risk,
            requires_approval=True,
            action_id=spec.action_id,
        )

    # 4순위: none/low → allow
    if risk in _ALLOW_RISK_LEVELS:
        return PolicyEvaluation(
            result=PolicyResult.allow,
            reason=f"위험도 '{risk}' — 정책 허용",
            risk_level=risk,
            requires_approval=False,
            action_id=spec.action_id,
        )

    # 기본값: 안전 우선 deny
    return PolicyEvaluation(
        result=PolicyResult.deny,
        reason=f"분류되지 않은 상태 — 안전 우선 차단",
        risk_level=risk,
        requires_approval=True,
        action_id=spec.action_id,
    )
