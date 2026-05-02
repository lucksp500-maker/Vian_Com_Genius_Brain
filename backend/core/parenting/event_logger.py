"""
EventLogger — WO-006
CommandOS 명령 실행 이벤트를 parenting_events.jsonl에 기록합니다.
모든 명령 실행 = AI 양육 데이터.

흐름:
    audit_ledger.py → log_event() → parenting_events.jsonl
    (Push 방식: audit_ledger가 직접 호출)
"""
from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# [의존성] 연결: audit_ledger.py (push caller) / 단독 수정 금지
_EVENTS_PATH = Path(__file__).parent.parent.parent / "data" / "parenting_events.jsonl"


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def _append_event_sync(event: dict, events_path: Path) -> None:
    """이벤트를 JSONL 파일에 append. 동기 함수 — to_thread로 호출."""
    _ensure_parent(events_path)
    line = json.dumps(event, ensure_ascii=False) + "\n"
    with open(str(events_path), "a", encoding="utf-8") as f:
        f.write(line)


def build_parenting_event(
    raw_input: str,
    action_spec_id: str,
    intent_class: str,
    risk_class: str,
    guard_result: Optional[str],
    approval_state: str,
    execution_state: str,
    user: str = "lucksp500",
    input_source: str = "hud",
    confidence: Optional[float] = None,
    lesson: Optional[str] = None,
) -> dict:
    """
    Parenting Event 딕셔너리를 생성합니다.

    설계도 섹션 H 기반 스키마:
        event_id, timestamp, input_source, raw_input, action_spec_id,
        intent_class, risk_class, initial_decision, confidence,
        guard_result, approval_state, execution_state, user_action,
        feedback_class, lesson, next_rule_candidate
    """
    initial_decision = (
        "allow" if risk_class in ("none", "low") else "ask"
    )
    feedback_class = _classify_feedback(execution_state, approval_state)

    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_source": input_source,
        "raw_input": raw_input,
        "action_spec_id": action_spec_id,
        "intent_class": intent_class,
        "risk_class": risk_class,
        "initial_decision": initial_decision,
        "confidence": confidence,
        "guard_result": guard_result,
        "approval_state": approval_state,
        "execution_state": execution_state,
        "user_action": approval_state,
        "feedback_class": feedback_class,
        "lesson": lesson,
        "next_rule_candidate": None,   # PatternAbstraction이 추후 채움
    }


def _classify_feedback(execution_state: str, approval_state: str) -> str:
    """실행 상태 기반 피드백 분류."""
    if execution_state == "executed":
        return "positive"
    if execution_state == "failed":
        return "negative"
    if approval_state == "user_rejected":
        return "rejected"
    return "neutral"


class EventLogger:
    """
    Parenting Event 기록기.

    사용:
        logger = EventLogger()
        await logger.log_event(event_dict)
    """

    def __init__(self, events_path: Optional[Path] = None):
        self._events_path = events_path or _EVENTS_PATH

    async def log_event(self, event: dict) -> None:
        """이벤트를 parenting_events.jsonl에 비동기로 기록합니다."""
        await asyncio.to_thread(_append_event_sync, event, self._events_path)

    async def read_recent(self, limit: int = 50) -> list[dict]:
        """최근 N개 이벤트를 반환합니다."""
        def _read_sync(path: Path, n: int) -> list[dict]:
            if not path.exists():
                return []
            events = []
            try:
                with open(str(path), "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                events.append(json.loads(line))
                            except json.JSONDecodeError:
                                continue
            except (PermissionError, OSError):
                return []
            return events[-n:]

        return await asyncio.to_thread(_read_sync, self._events_path, limit)
