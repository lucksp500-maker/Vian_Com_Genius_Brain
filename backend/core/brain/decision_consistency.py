"""
DecisionConsistencyEngine — WO-005
같은 입력에 대해 일관된 intent_class/risk_class/reason_hash를 유지하는지 측정합니다.
결과는 decision_fingerprints.sqlite에 저장됩니다.

흐름:
    ActionSpec + Ground Truth Seed → fingerprint 생성 → 과거 fingerprint 비교
    → consistency_score (0.0~1.0) + conflict_detected (bool)
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import sqlite3
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from backend.core.commandos.action_spec import ActionSpec

# [의존성] 연결: commandos_brain_router.py / 단독 수정 금지
_DB_PATH = Path(__file__).parent.parent.parent / "data" / "decision_fingerprints.sqlite"

# H-02 Fix: TOCTOU race condition 방지 — SELECT+INSERT 원자적 실행 보장
# RLock 사용 이유: 재진입 안전 (같은 스레드 내 중첩 호출 허용)
_FP_LOCK = threading.RLock()

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS decision_fingerprints (
    fingerprint_id  TEXT PRIMARY KEY,
    input_hash      TEXT NOT NULL,
    intent_class    TEXT NOT NULL,
    risk_class      TEXT NOT NULL,
    decision_hash   TEXT NOT NULL,
    reason_hash     TEXT NOT NULL,
    repeat_count    INTEGER NOT NULL DEFAULT 1,
    consistency_score REAL NOT NULL DEFAULT 1.0,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_fp_input_hash ON decision_fingerprints(input_hash);
"""


def _init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    try:
        # H-09 Fix: WAL 모드 — 동시 읽기/쓰기 성능 개선 + 'database is locked' 방지
        conn.execute("PRAGMA journal_mode=WAL")
        conn.executescript(_CREATE_SQL)
        conn.commit()
    finally:
        conn.close()


@dataclass
class ConsistencyResult:
    """
    Decision Consistency Engine 출력.

    consistency_score: 1.0 = 완전 일관, 0.0 = 완전 불일치
    conflict_detected: Ground Truth Seed와 충돌 여부
    recommended_action: 기존 일관된 결정 또는 현재 결정
    """
    fingerprint_id: str
    input_hash: str
    intent_class: str
    risk_class: str
    consistency_score: float
    repeat_count: int
    conflict_detected: bool
    recommended_action: str   # "allow" | "deny" | "ask"


def _compute_input_hash(raw_input: str) -> str:
    """입력 텍스트의 SHA256 해시 (앞 16자)."""
    return hashlib.sha256(raw_input.strip().lower().encode()).hexdigest()[:16]


def _compute_reason_hash(intent: str, risk: str) -> str:
    """intent + risk 조합 해시."""
    return hashlib.sha256(f"{intent}|{risk}".encode()).hexdigest()[:16]


def _get_or_create_fingerprint_sync(
    input_hash: str,
    intent_class: str,
    risk_class: str,
    reason_hash: str,
    db_path: Path,
) -> ConsistencyResult:
    """DB에서 fingerprint를 조회하고, 없으면 생성합니다. 동기 함수."""
    # H-02 Fix: RLock으로 SELECT+INSERT 원자적 실행 — TOCTOU race condition 방지
    with _FP_LOCK:
        return _get_or_create_fingerprint_locked(
            input_hash, intent_class, risk_class, reason_hash, db_path
        )


def _get_or_create_fingerprint_locked(
    input_hash: str,
    intent_class: str,
    risk_class: str,
    reason_hash: str,
    db_path: Path,
) -> ConsistencyResult:
    """_FP_LOCK 획득 상태에서 호출되는 실제 DB 작업."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    now = datetime.now(timezone.utc).isoformat()

    try:
        row = conn.execute(
            "SELECT * FROM decision_fingerprints WHERE input_hash = ? LIMIT 1",
            (input_hash,),
        ).fetchone()

        if row is None:
            # 최초 입력 — fingerprint 생성
            # H-02 Fix: INSERT OR IGNORE — UNIQUE INDEX 위반 시 무시 후 재조회
            # (RLock으로 같은 프로세스 내 race 차단, UNIQUE INDEX로 DB 수준 중복 방지)
            fp_id = hashlib.sha256(f"{input_hash}|{now}".encode()).hexdigest()[:24]
            try:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO decision_fingerprints
                        (fingerprint_id, input_hash, intent_class, risk_class,
                         decision_hash, reason_hash, repeat_count, consistency_score,
                         created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, 1, 1.0, ?, ?)
                    """,
                    (fp_id, input_hash, intent_class, risk_class,
                     reason_hash, reason_hash, now, now),
                )
                conn.commit()
            except sqlite3.IntegrityError:
                conn.rollback()

            # INSERT OR IGNORE 후 재조회 — 다른 연결이 먼저 삽입한 row 사용
            row = conn.execute(
                "SELECT * FROM decision_fingerprints WHERE input_hash = ? LIMIT 1",
                (input_hash,),
            ).fetchone()

            if row is None:
                # 재조회도 None이면 DB 오류 — 방어적 반환
                return ConsistencyResult(
                    fingerprint_id=fp_id,
                    input_hash=input_hash,
                    intent_class=intent_class,
                    risk_class=risk_class,
                    consistency_score=1.0,
                    repeat_count=1,
                    conflict_detected=False,
                    recommended_action=_risk_to_action(risk_class),
                )

            return ConsistencyResult(
                fingerprint_id=row["fingerprint_id"],
                input_hash=input_hash,
                intent_class=row["intent_class"],
                risk_class=row["risk_class"],
                consistency_score=row["consistency_score"],
                repeat_count=row["repeat_count"],
                conflict_detected=False,
                recommended_action=_risk_to_action(row["risk_class"]),
            )
        else:
            # 기존 fingerprint — 일관성 비교
            stored_reason = row["reason_hash"]
            stored_intent = row["intent_class"]
            stored_risk = row["risk_class"]
            repeat = row["repeat_count"] + 1

            # 동일 reason_hash이면 완전 일관 (score 유지 또는 증가)
            if reason_hash == stored_reason:
                new_score = min(1.0, row["consistency_score"] + 0.05)
                conflict = False
            else:
                # 불일치 — score 감소
                new_score = max(0.0, row["consistency_score"] - 0.2)
                conflict = True

            conn.execute(
                """
                UPDATE decision_fingerprints
                SET intent_class=?, risk_class=?, decision_hash=?, reason_hash=?,
                    repeat_count=?, consistency_score=?, updated_at=?
                WHERE input_hash=?
                """,
                (intent_class, risk_class, reason_hash, reason_hash,
                 repeat, new_score, now, input_hash),
            )
            conn.commit()

            return ConsistencyResult(
                fingerprint_id=row["fingerprint_id"],
                input_hash=input_hash,
                intent_class=stored_intent if not conflict else intent_class,
                risk_class=stored_risk if not conflict else risk_class,
                consistency_score=new_score,
                repeat_count=repeat,
                conflict_detected=conflict,
                recommended_action=_risk_to_action(stored_risk if not conflict else risk_class),
            )
    finally:
        conn.close()


def _risk_to_action(risk_class: str) -> str:
    if risk_class in ("high", "medium"):
        return "ask"
    if risk_class == "none":
        return "allow"
    return "allow"


class DecisionConsistencyEngine:
    """
    Decision Consistency Engine.

    같은 입력이 들어왔을 때 이전 판단과 비교하여 일관성 점수를 반환합니다.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or _DB_PATH
        _init_db(self._db_path)

    async def check(self, spec: ActionSpec) -> ConsistencyResult:
        """ActionSpec에 대한 일관성 결과를 반환합니다."""
        input_hash = _compute_input_hash(spec.raw_input)
        reason_hash = _compute_reason_hash(spec.intent, str(spec.risk_level))
        return await asyncio.to_thread(
            _get_or_create_fingerprint_sync,
            input_hash,
            spec.intent or "unknown",
            str(spec.risk_level),
            reason_hash,
            self._db_path,
        )
