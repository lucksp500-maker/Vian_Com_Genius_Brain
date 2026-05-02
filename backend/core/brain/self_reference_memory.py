"""
SelfReferenceMemoryEngine — WO-005
이전 판단/승인/취소/실패 기록을 현재 판단의 근거로 인용합니다.
parenting_events.jsonl에서 관련 이벤트를 조회합니다.

흐름:
    ActionSpec + parenting_events.jsonl → 유사 이벤트 검색
    → memory_citation (과거 event_id) + memory_weight + memory_conflict
"""
from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.core.commandos.action_spec import ActionSpec

# [의존성] 연결: commandos_brain_router.py / 단독 수정 금지
_EVENTS_PATH = Path(__file__).parent.parent.parent / "data" / "parenting_events.jsonl"

# 시간 감쇠 반감기 — 30일이면 가중치 0.5
_HALF_LIFE_DAYS = 30.0
_MEMORY_WINDOW = 100  # 최근 N개 이벤트만 검색


@dataclass
class MemoryCitation:
    """
    Self-Reference Memory 출력.

    prior_event_id: 인용한 과거 이벤트 ID (없으면 None)
    memory_weight: 인용 강도 (0.0~1.0, 시간 감쇠 적용)
    memory_conflict: 과거와 다른 결정 필요 여부
    lesson: 과거 실패에서 추출된 교훈 (있으면)
    """
    prior_event_id: Optional[str]
    prior_intent_class: Optional[str]
    prior_execution_state: Optional[str]
    memory_weight: float
    memory_conflict: bool
    lesson: Optional[str]
    cold_start: bool   # True이면 참조할 과거 기록 없음


def _compute_time_decay(event_ts: str, now: datetime) -> float:
    """이벤트 타임스탬프 기반 시간 감쇠 가중치 계산."""
    try:
        event_dt = datetime.fromisoformat(event_ts.replace("Z", "+00:00"))
        days_ago = (now - event_dt).total_seconds() / 86400.0
        return max(0.01, 0.5 ** (days_ago / _HALF_LIFE_DAYS))
    except Exception:
        return 0.1


def _find_memory_sync(raw_input: str, intent: str, events_path: Path) -> MemoryCitation:
    """parenting_events.jsonl에서 유사 이벤트를 찾아 인용합니다. 동기 함수."""
    if not events_path.exists():
        return MemoryCitation(
            prior_event_id=None,
            prior_intent_class=None,
            prior_execution_state=None,
            memory_weight=0.0,
            memory_conflict=False,
            lesson=None,
            cold_start=True,
        )

    now = datetime.now(timezone.utc)
    events: list[dict] = []

    try:
        with open(str(events_path), "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        events.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    except (PermissionError, OSError):
        return MemoryCitation(
            prior_event_id=None, prior_intent_class=None,
            prior_execution_state=None, memory_weight=0.0,
            memory_conflict=False, lesson=None, cold_start=True,
        )

    if not events:
        return MemoryCitation(
            prior_event_id=None, prior_intent_class=None,
            prior_execution_state=None, memory_weight=0.0,
            memory_conflict=False, lesson=None, cold_start=True,
        )

    # 최근 _MEMORY_WINDOW개만 검색
    recent = events[-_MEMORY_WINDOW:]

    # 키워드 매칭 — raw_input의 첫 단어들로 유사 이벤트 찾기
    keywords = set(raw_input.lower().split()[:5])
    best_match: Optional[dict] = None
    best_weight = 0.0

    for ev in reversed(recent):
        ev_input = ev.get("raw_input", "").lower()
        ev_intent = ev.get("intent_class", "")
        ev_ts = ev.get("timestamp", "")

        # 의도 클래스 일치 또는 키워드 겹침
        intent_match = bool(intent and ev_intent and intent[:20] == ev_intent[:20])
        keyword_overlap = len(keywords & set(ev_input.split()[:5])) / max(len(keywords), 1)
        relevance = (0.5 if intent_match else 0.0) + keyword_overlap * 0.5

        if relevance > 0.3:
            decay = _compute_time_decay(ev_ts, now)
            weight = relevance * decay
            if weight > best_weight:
                best_weight = weight
                best_match = ev

    if best_match is None:
        return MemoryCitation(
            prior_event_id=None, prior_intent_class=None,
            prior_execution_state=None, memory_weight=0.0,
            memory_conflict=False, lesson=None, cold_start=False,
        )

    prior_state = best_match.get("execution_state", "")
    lesson = best_match.get("lesson") if prior_state == "failed" else None
    # 이전에 실패했고 같은 입력이 들어오면 conflict
    memory_conflict = prior_state in ("failed", "user_rejected")

    return MemoryCitation(
        prior_event_id=best_match.get("event_id"),
        prior_intent_class=best_match.get("intent_class"),
        prior_execution_state=prior_state,
        memory_weight=round(best_weight, 3),
        memory_conflict=memory_conflict,
        lesson=lesson,
        cold_start=False,
    )


class SelfReferenceMemoryEngine:
    """
    Self-Reference Memory Engine.

    parenting_events.jsonl에서 과거 판단을 인용하여 현재 판단 근거를 제공합니다.
    """

    def __init__(self, events_path: Optional[Path] = None):
        self._events_path = events_path or _EVENTS_PATH

    async def cite(self, spec: ActionSpec) -> MemoryCitation:
        """ActionSpec에 관련된 과거 이벤트를 인용합니다."""
        return await asyncio.to_thread(
            _find_memory_sync,
            spec.raw_input,
            spec.intent or "",
            self._events_path,
        )
