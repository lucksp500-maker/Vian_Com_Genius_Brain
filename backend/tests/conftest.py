"""
conftest.py — 전역 테스트 픽스처
I-06 Fix: Brain Router 모듈 레벨 싱글턴 — 프로덕션 DB 오염 방지
          _consistency_engine / _memory_engine이 임시 DB를 사용하도록 패치

NC-06 (테스트 DB 격리 누락)를 E2E 뿐 아니라 전체 테스트에 적용.
모든 테스트에서 brain router 싱글턴이 tmp DB를 사용하여 프로덕션 DB 오염을 방지합니다.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from backend.core.brain.decision_consistency import DecisionConsistencyEngine
from backend.core.brain.self_reference_memory import SelfReferenceMemoryEngine


@pytest.fixture(autouse=True)
def _isolate_brain_router_db(tmp_path: Path):
    """
    I-06 Fix: Brain Router 모듈 레벨 싱글턴을 임시 DB 인스턴스로 교체.
    테스트 후 자동 삭제되므로 프로덕션 decision_fingerprints.sqlite / self_reference_memory.sqlite
    에 테스트 데이터가 기록되지 않습니다.
    """
    import backend.core.brain.commandos_brain_router as router_module

    tmp_consistency_engine = DecisionConsistencyEngine(
        db_path=tmp_path / "test_decision_fingerprints.sqlite"
    )
    tmp_memory_engine = SelfReferenceMemoryEngine(
        events_path=tmp_path / "test_parenting_events.jsonl"
    )

    with (
        patch.object(router_module, "_consistency_engine", tmp_consistency_engine),
        patch.object(router_module, "_memory_engine", tmp_memory_engine),
    ):
        yield
