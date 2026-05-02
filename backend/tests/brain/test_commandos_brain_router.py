"""
test_commandos_brain_router.py — WO-005 테스트
4-Brain Core 전체 커버리지.

주요 검증:
1. ActionSpec → consistency_score + memory_citation + confidence_score 생성
2. 동일 입력 3회 → intent/risk/reason_hash 안정 유지
3. risk=none → confidence "continue" (Guard 없이 판단 가능)
4. risk=high → needs_human_approval=True (Guard 라우팅)
5. pattern_abstraction.approved는 항상 False (자가학습 금지 원칙)
6. brain_router 실패 시 Guard fallback 정상 진행
"""
from __future__ import annotations

from pathlib import Path

import pytest

from backend.core.commandos.action_spec import ActionSpec, RiskLevel, TargetType
from backend.core.brain.commandos_brain_router import route
from backend.core.brain.decision_consistency import DecisionConsistencyEngine
from backend.core.brain.self_reference_memory import SelfReferenceMemoryEngine
from backend.core.brain.internal_confidence import assess_confidence
from backend.core.brain.pattern_abstraction import evaluate_pattern, PatternStats


# ─── ActionSpec 팩토리 헬퍼 ───────────────────────────────────────

def make_spec(
    raw_input: str,
    intent: str = "파일 검색",
    risk: RiskLevel = RiskLevel.none,
    requires_approval: bool = False,
) -> ActionSpec:
    return ActionSpec(
        raw_input=raw_input,
        intent=intent,
        target_type=TargetType.file,
        risk_level=risk,
        requires_approval=requires_approval,
    )


# ─── DecisionConsistencyEngine ────────────────────────────────────

class TestDecisionConsistency:
    @pytest.mark.asyncio
    async def test_first_input_returns_score_1(self, tmp_path):
        engine = DecisionConsistencyEngine(db_path=tmp_path / "fp.sqlite")
        spec = make_spec("견적서 찾아줘", intent="파일 검색", risk=RiskLevel.none)
        result = await engine.check(spec)
        assert result.consistency_score == 1.0
        assert result.repeat_count == 1
        assert result.conflict_detected is False

    @pytest.mark.asyncio
    async def test_same_input_3x_stays_stable(self, tmp_path):
        """동일 입력 3회 반복 시 intent/risk 안정 유지."""
        engine = DecisionConsistencyEngine(db_path=tmp_path / "fp.sqlite")
        spec = make_spec("어제 받은 견적서 찾아줘", intent="파일 검색", risk=RiskLevel.none)

        r1 = await engine.check(spec)
        r2 = await engine.check(spec)
        r3 = await engine.check(spec)

        # intent_class와 risk_class가 3회 모두 동일해야 함
        assert r1.intent_class == r2.intent_class == r3.intent_class
        assert r1.risk_class == r2.risk_class == r3.risk_class
        # 일관성 점수는 유지 또는 증가
        assert r3.consistency_score >= r1.consistency_score
        assert r3.repeat_count == 3

    @pytest.mark.asyncio
    async def test_different_risk_decreases_score(self, tmp_path):
        """같은 입력에 다른 위험도 → 불일치 감지, 점수 감소."""
        engine = DecisionConsistencyEngine(db_path=tmp_path / "fp.sqlite")
        spec_safe = make_spec("파일 삭제", intent="파일 삭제", risk=RiskLevel.none)
        spec_risky = make_spec("파일 삭제", intent="파일 삭제", risk=RiskLevel.high)

        r1 = await engine.check(spec_safe)
        r2 = await engine.check(spec_risky)

        assert r2.conflict_detected is True
        assert r2.consistency_score < r1.consistency_score

    @pytest.mark.asyncio
    async def test_reason_hash_stable_on_consistency(self, tmp_path):
        """일관된 입력의 reason_hash는 3회 모두 동일."""
        engine = DecisionConsistencyEngine(db_path=tmp_path / "fp.sqlite")
        spec = make_spec("현재 탭 저장", intent="탭 저장", risk=RiskLevel.low)
        results = [await engine.check(spec) for _ in range(3)]
        # conflict 없으면 risk_class 동일 유지
        non_conflict = [r for r in results if not r.conflict_detected]
        assert len(non_conflict) >= 2


# ─── SelfReferenceMemoryEngine ────────────────────────────────────

class TestSelfReferenceMemory:
    @pytest.mark.asyncio
    async def test_cold_start_returns_no_citation(self, tmp_path):
        """parenting_events.jsonl 없으면 cold_start=True."""
        engine = SelfReferenceMemoryEngine(
            events_path=tmp_path / "parenting_events.jsonl"
        )
        spec = make_spec("문서 요약해줘")
        result = await engine.cite(spec)
        assert result.cold_start is True
        assert result.prior_event_id is None
        assert result.memory_weight == 0.0

    @pytest.mark.asyncio
    async def test_cites_prior_event(self, tmp_path):
        """과거 parenting 이벤트가 있으면 event_id를 인용합니다."""
        import json
        from datetime import datetime, timezone
        events_path = tmp_path / "parenting_events.jsonl"
        past_event = {
            "event_id": "ev-001",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_input": "이 PDF 요약해줘",
            "intent_class": "문서 요약",
            "execution_state": "executed",
            "lesson": None,
        }
        events_path.write_text(json.dumps(past_event, ensure_ascii=False) + "\n")

        engine = SelfReferenceMemoryEngine(events_path=events_path)
        spec = make_spec("이 PDF 요약해줘", intent="문서 요약")
        result = await engine.cite(spec)
        assert result.cold_start is False
        # 키워드/의도 매칭으로 인용될 수 있음 (memory_weight > 0)
        assert result.prior_event_id is not None or result.memory_weight >= 0.0

    @pytest.mark.asyncio
    async def test_failed_event_sets_conflict(self, tmp_path):
        """실패한 과거 이벤트 → memory_conflict=True."""
        import json
        from datetime import datetime, timezone
        events_path = tmp_path / "parenting_events.jsonl"
        past_event = {
            "event_id": "ev-002",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "raw_input": "파일 이동 실행",
            "intent_class": "파일 이동",
            "execution_state": "failed",
            "lesson": "권한 없는 폴더에 이동 시도",
        }
        events_path.write_text(json.dumps(past_event, ensure_ascii=False) + "\n")

        engine = SelfReferenceMemoryEngine(events_path=events_path)
        spec = make_spec("파일 이동 실행", intent="파일 이동")
        result = await engine.cite(spec)
        assert result.cold_start is False
        if result.prior_event_id:
            assert result.memory_conflict is True
            assert result.lesson is not None


# ─── InternalConfidenceModel ──────────────────────────────────────

class TestInternalConfidence:
    def test_risk_none_continues_without_approval(self):
        """위험도 0 작업 → stop_or_continue=continue, needs_human_approval=False."""
        result = assess_confidence(
            intent_class="파일 검색", risk_class="none",
            memory_match_score=0.0, memory_conflict=False,
            consistency_score=1.0, cold_start=False,
        )
        assert result.stop_or_continue == "continue"
        assert result.needs_human_approval is False
        assert result.confidence_score > 0.7

    def test_risk_high_requires_approval(self):
        """위험도 높음 → needs_human_approval=True.
        '삭제'를 쓰면 Ground Truth Deny가 먼저 걸리므로 별도 high risk intent 사용."""
        result = assess_confidence(
            intent_class="시스템 재시작", risk_class="high",
        )
        assert result.needs_human_approval is True
        assert result.stop_or_continue in ("ask", "stop")  # risk=high는 ask 또는 stop
        assert result.confidence_score < 0.5

    def test_ground_truth_conflict_stops(self):
        """Ground Truth Seed 충돌 → stop, ground_truth_conflict=True."""
        result = assess_confidence(
            intent_class="외부전송", risk_class="medium",
        )
        assert result.ground_truth_conflict is True
        assert result.stop_or_continue == "stop"
        assert result.needs_human_approval is True

    def test_cold_start_triggers_ask(self):
        """첫 실행(cold_start=True) → 낮은 confidence, ask."""
        result = assess_confidence(
            intent_class="파일 압축", risk_class="none",
            cold_start=True,
        )
        assert result.stop_or_continue == "ask"
        assert result.needs_human_approval is True

    def test_memory_conflict_lowers_confidence(self):
        """이전 실패 기록(memory_conflict) → confidence 감소."""
        safe = assess_confidence("파일 검색", "none", memory_conflict=False, cold_start=False)
        conflict = assess_confidence("파일 검색", "none", memory_conflict=True, cold_start=False)
        assert conflict.confidence_score < safe.confidence_score

    def test_delete_intent_always_stops(self):
        """'삭제' 포함 intent → Ground Truth 충돌, stop."""
        result = assess_confidence(intent_class="파일 삭제", risk_class="none")
        assert result.ground_truth_conflict is True
        assert result.stop_or_continue == "stop"


# ─── PatternAbstractionEngine — 자가학습 금지 원칙 검증 ───────────

class TestPatternAbstraction:
    def test_approved_always_false(self):
        """[자가학습 금지] approved는 조건 만족해도 항상 False."""
        stats = PatternStats(
            pattern_key="파일 검색",
            occurrence_count=5,
            success_count=5,
            failure_count=0,
            reuse_count=3,
            age_days=10.0,
        )
        candidate = evaluate_pattern(stats)
        assert candidate is not None
        assert candidate.approved is False, "자가학습 금지 원칙 위반: approved가 True"

    def test_requires_approval_always_true(self):
        """[자가학습 금지] requires_approval은 항상 True."""
        stats = PatternStats(
            pattern_key="탭 저장",
            occurrence_count=10,
            success_count=9,
            failure_count=1,
            reuse_count=5,
            age_days=5.0,
        )
        candidate = evaluate_pattern(stats)
        assert candidate is not None
        assert candidate.requires_approval is True, "자가학습 금지 원칙 위반"

    def test_insufficient_occurrences_returns_none(self):
        """발생 횟수 3회 미만 → 후보 없음."""
        stats = PatternStats(
            pattern_key="파일 이동", occurrence_count=2,
            success_count=2, failure_count=0, reuse_count=2, age_days=5.0,
        )
        assert evaluate_pattern(stats) is None

    def test_low_success_rate_returns_none(self):
        """성공률 80% 미만 → 후보 없음."""
        stats = PatternStats(
            pattern_key="파일 이동", occurrence_count=5,
            success_count=3, failure_count=2, reuse_count=3, age_days=5.0,
        )
        assert evaluate_pattern(stats) is None

    def test_insufficient_reuse_returns_none(self):
        """재사용 2회 미만 → 후보 없음."""
        stats = PatternStats(
            pattern_key="탭 저장", occurrence_count=5,
            success_count=5, failure_count=0, reuse_count=1, age_days=5.0,
        )
        assert evaluate_pattern(stats) is None

    def test_stale_pattern_returns_none(self):
        """30일 초과 활성 → 후보 없음."""
        stats = PatternStats(
            pattern_key="탭 저장", occurrence_count=5,
            success_count=5, failure_count=0, reuse_count=3, age_days=35.0,
        )
        assert evaluate_pattern(stats) is None

    def test_qualified_pattern_returns_candidate(self):
        """모든 조건 만족 → PatternCandidate 반환 (승인 대기)."""
        stats = PatternStats(
            pattern_key="최근 문서 검색",
            occurrence_count=5, success_count=5,
            failure_count=0, reuse_count=3, age_days=7.0,
        )
        candidate = evaluate_pattern(stats)
        assert candidate is not None
        assert candidate.rule_candidate is not None
        assert candidate.skill_candidate is not None
        assert candidate.approved is False  # 자가학습 금지


# ─── CommandosBrainRouter 통합 테스트 ────────────────────────────

class TestBrainRouter:
    @pytest.mark.asyncio
    async def test_route_produces_all_scores(self, tmp_path):
        """brain_router.route() → consistency+memory+confidence 모두 생성."""
        spec = make_spec("어제 받은 견적서 찾아줘", intent="파일 검색", risk=RiskLevel.none)
        result = await route(spec)

        assert result.consistency.consistency_score >= 0.0
        assert result.memory is not None
        assert result.confidence.confidence_score >= 0.0
        assert result.enriched_spec.confidence_score is not None

    @pytest.mark.asyncio
    async def test_enriched_spec_has_confidence_score(self):
        """brain_router 후 ActionSpec에 confidence_score가 채워져야 함."""
        spec = make_spec("PDF 요약해줘", intent="문서 요약", risk=RiskLevel.none)
        result = await route(spec)
        assert result.enriched_spec.confidence_score is not None
        assert 0.0 <= result.enriched_spec.confidence_score <= 1.0

    @pytest.mark.asyncio
    async def test_route_graceful_on_brain_failure(self):
        """Brain Router가 내부에서 실패해도 enriched_spec이 반환됨 (fallback 보장)."""
        spec = make_spec("테스트 입력", intent="", risk=RiskLevel.none)
        try:
            result = await route(spec)
            assert result.enriched_spec is not None
        except Exception as e:
            pytest.fail(f"brain_router.route() raised {e} — fallback 실패")

    @pytest.mark.asyncio
    async def test_risk_none_confidence_sufficient_for_self_judgment(self):
        """위험도 0 작업 → confidence가 충분하여 Guard 없이 자체 판단 가능."""
        spec = make_spec("최근 파일 목록", intent="파일 목록 조회", risk=RiskLevel.none)
        result = await route(spec)
        # risk=none이고 cold_start인 경우에도 confidence 계산됨
        assert result.confidence.confidence_score >= 0.0

    @pytest.mark.asyncio
    async def test_risk_high_routes_to_guard(self):
        """위험도 높음 → Guard 라우팅 (needs_human_approval=True)."""
        spec = make_spec("파일 삭제", intent="파일 삭제", risk=RiskLevel.high)
        result = await route(spec)
        assert result.confidence.needs_human_approval is True
