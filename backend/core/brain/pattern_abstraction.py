"""
PatternAbstractionEngine — WO-005
반복 성공 패턴을 규칙 후보와 스킬 후보로 승격합니다.

중요: 자가학습 절대 금지 원칙
- 이 엔진은 후보(candidate)를 생성할 뿐입니다.
- Pattern Memory에 자동으로 삽입하지 않습니다.
- 모든 후보는 사용자 승인 후에만 적용됩니다.

승격 조건 (모두 만족 필요):
  - 동일 패턴 3회 이상
  - 성공률 80% 이상 (success_count / total >= 0.8)
  - 재사용 2회 이상
  - 30일 이내 활성

흐름:
    parenting_events 통계 → 조건 평가 → PatternCandidate (승인 대기)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

# [보호] 이유: 자가학습 절대 금지 — Pattern Memory 직접 삽입 코드 추가 금지
# 수정 필요 시: 현인님 승인 후 별도 파일(pattern_memory_writer.py)에서만 처리

_MIN_OCCURRENCES = 3
_MIN_SUCCESS_RATE = 0.8
_MIN_REUSE_COUNT = 2
_MAX_AGE_DAYS = 30


@dataclass
class PatternCandidate:
    """
    Pattern Abstraction Engine 출력 — 승인 대기 후보.

    approved: 항상 False (자동 승격 금지)
    requires_approval: 항상 True
    """
    pattern_key: str
    occurrence_count: int
    success_count: int
    failure_count: int
    reuse_count: int
    success_rate: float
    rule_candidate: Optional[str]   # 생성된 규칙 후보 텍스트
    skill_candidate: Optional[str]  # 생성된 스킬 후보 이름
    counterexample: Optional[str]   # 반례 설명
    approved: bool = False           # [보호] 항상 False — 자가학습 금지
    requires_approval: bool = True   # [보호] 항상 True — 자가학습 금지
    promotion_blocked_reason: Optional[str] = None  # 승격 차단 이유


@dataclass
class PatternStats:
    """입력 통계 데이터."""
    pattern_key: str
    occurrence_count: int
    success_count: int
    failure_count: int
    reuse_count: int
    age_days: float
    counterexample: Optional[str] = None


def evaluate_pattern(stats: PatternStats) -> Optional[PatternCandidate]:
    """
    패턴 통계를 평가하여 승격 후보를 생성합니다.
    조건 미달 시 None 반환.

    [보호] 이유: 자가학습 금지 — 이 함수는 후보만 생성하고 저장하지 않습니다.
    수정 필요 시: 현인님 승인 필수.
    """
    total = stats.occurrence_count
    if total == 0:
        return None

    success_rate = stats.success_count / total

    # 승격 조건 검사
    blocked_reasons: list[str] = []

    if total < _MIN_OCCURRENCES:
        blocked_reasons.append(f"발생 횟수 부족 ({total}/{_MIN_OCCURRENCES})")
    if success_rate < _MIN_SUCCESS_RATE:
        blocked_reasons.append(f"성공률 부족 ({success_rate:.0%}/{_MIN_SUCCESS_RATE:.0%})")
    if stats.reuse_count < _MIN_REUSE_COUNT:
        blocked_reasons.append(f"재사용 횟수 부족 ({stats.reuse_count}/{_MIN_REUSE_COUNT})")
    if stats.age_days > _MAX_AGE_DAYS:
        blocked_reasons.append(f"활성 기간 초과 ({stats.age_days:.0f}일/{_MAX_AGE_DAYS}일)")

    if blocked_reasons:
        # 조건 미달 — 후보 없음
        return None

    # 모든 조건 만족 — 후보 생성 (승인 대기)
    rule_text = (
        f"패턴 '{stats.pattern_key}'는 {total}회 발생, "
        f"성공률 {success_rate:.0%} — 자동 실행 후보"
    )
    skill_name = (
        "auto_" + stats.pattern_key.lower().replace(" ", "_")[:30]
    )

    return PatternCandidate(
        pattern_key=stats.pattern_key,
        occurrence_count=total,
        success_count=stats.success_count,
        failure_count=stats.failure_count,
        reuse_count=stats.reuse_count,
        success_rate=round(success_rate, 3),
        rule_candidate=rule_text,
        skill_candidate=skill_name,
        counterexample=stats.counterexample,
        approved=False,          # [보호] 자가학습 금지 — 절대 True로 변경하지 말 것
        requires_approval=True,  # [보호] 자가학습 금지 — 절대 False로 변경하지 말 것
        promotion_blocked_reason=None,
    )
