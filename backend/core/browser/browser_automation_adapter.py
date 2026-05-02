"""
BrowserAutomationAdapter — WO-007 (양방향 브리지)
HUD → Guard → 백엔드 큐 → Extension 명령 → DOM 추출 → 백엔드 수신 → Archive

아키텍처 (양방향):

  [송신] CommandHUD → ActionSpec → Guard 승인
           → BrowserAutomationAdapter.dispatch() → PendingCommand 큐 등록
           → Extension polls GET /api/v1/browser/queue/next
           → content script EXTRACT_AND_SEND
           → background POST /api/v1/browser/result

  [수신] BrowserAutomationAdapter.receive_result()
           → PromptInjectionShield 스캔
           → Archive 저장 / AuditLedger 기록

지원 action_type:
    save_tab   — 현재 탭 본문 저장 (risk=low, requires_approval=True)
    summarize  — 현재 페이지 요약 (risk=none, requires_approval=False)
    collect    — 브라우저 자료 수집 (risk=low, requires_approval=True)

큐 구현:
    V1 = in-memory dict (로컬 1인 운영, 재시작 시 초기화 허용)
    TTL = 60초 (Extension이 60초 내 폴링하지 않으면 만료)

[보호] 이유: Extension ↔ Backend 양방향 경계 / 수정 필요 시: 큐 방식(메모리→Redis) 교체 가능
[의존성] 연결: prompt_injection_shield.scan() / action_spec.ActionSpec / browser_router / 단독 수정 금지
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Optional

from backend.core.commandos.action_spec import (
    ActionSource,
    ActionSpec,
    ExecutionState,
    RiskLevel,
    TargetType,
)
from backend.core.security.prompt_injection_shield import PromptInjectionShield

# ─── 정책 매핑 ──────────────────────────────────────────────────

_ACTION_POLICY: dict[str, tuple[RiskLevel, bool]] = {
    "save_tab":  (RiskLevel.low,  True),   # 저장 = 승인 필요
    "summarize": (RiskLevel.none, False),  # 요약 = 즉시 실행
    "collect":   (RiskLevel.low,  True),   # 수집 = 승인 필요
}

_COMMAND_TTL_SECONDS = 60  # 명령 유효 시간

# H-05 Fix: dispatch() 허용 execution_state 목록
# guard_approved 또는 user_approved 상태만 Extension 큐 등록 허용
_ALLOWED_EXEC_STATES: frozenset[str] = frozenset({
    ExecutionState.guard_approved.value,
    ExecutionState.user_approved.value,
})


# ─── 데이터 타입 ─────────────────────────────────────────────────

@dataclass
class PendingCommand:
    """
    백엔드 → Extension 방향 명령.
    큐에 등록되어 Extension이 poll로 가져갑니다.
    """
    command_id: str
    action_type: str          # "save_tab" | "summarize" | "collect"
    action_spec_id: str       # Guard 승인된 ActionSpec의 ID
    expires_at: datetime


@dataclass
class BrowserResult:
    """
    Extension → 백엔드 방향 DOM 추출 결과.
    POST /api/v1/browser/result 로 전송됩니다.
    """
    command_id: str
    action_type: str
    url: str
    title: str
    raw_content: str
    meta_description: str = ""
    word_count: int = 0


@dataclass
class DispatchResult:
    """
    dispatch() 반환값 — 명령 큐 등록 결과.
    """
    command_id: str
    action_spec: ActionSpec
    queued: bool
    reason: str = ""


@dataclass
class ReceiveResult:
    """
    receive_result() 반환값 — DOM 수신 처리 결과.
    """
    success: bool
    blocked: bool = False
    block_reason: str = ""
    injection_risk: bool = False
    stored_content_length: int = 0


# ─── 어댑터 ─────────────────────────────────────────────────────

class BrowserAutomationAdapter:
    """
    양방향 브라우저 자동화 브리지.

    [송신] dispatch(action_spec)
        Guard 승인된 ActionSpec을 받아 PendingCommand로 큐에 등록.
        Extension이 GET /api/v1/browser/queue/next 로 폴링하여 수거.

    [수신] receive_result(result)
        Extension이 POST /api/v1/browser/result 로 전송한 DOM 데이터를 처리.
        PromptInjectionShield 스캔 후 저장.

    [직접 푸시] receive_push(payload)
        Extension 팝업이 직접 POST /api/v1/browser/collect 로 보내는 경우.
        Guard 미거친 경우 ActionSpec 생성 + Shield 스캔.
    """

    def __init__(self) -> None:
        self._shield = PromptInjectionShield()
        # command_id → PendingCommand (in-memory, V1)
        self._queue: dict[str, PendingCommand] = {}
        # H-04 Fix: pop-on-poll 데이터 손실 방지 — Extension ACK 전까지 명령 보존
        # Extension이 poll 후 result POST 완료 전 크래시 시 재전송 가능
        self._in_flight: dict[str, PendingCommand] = {}

    # ──────────────────── 송신 경로 ───────────────────────────────

    def dispatch(self, action_spec: ActionSpec) -> DispatchResult:
        """
        Guard 승인된 ActionSpec을 Extension 명령 큐에 등록합니다.

        action_spec.target_type 이 browser_tab 이어야 합니다.
        action_spec.execution_state 는 guard_approved 또는 user_approved 이어야 합니다.
        """
        # H-05 Fix: execution_state 검증 — 미승인 spec 큐 등록 차단
        if action_spec.execution_state not in _ALLOWED_EXEC_STATES:
            return DispatchResult(
                command_id="",
                action_spec=action_spec,
                queued=False,
                reason=(
                    f"execution_state '{action_spec.execution_state}'은 dispatch 불가 "
                    f"(허용: {sorted(_ALLOWED_EXEC_STATES)})"
                ),
            )

        if action_spec.target_type != TargetType.browser_tab.value:
            return DispatchResult(
                command_id="",
                action_spec=action_spec,
                queued=False,
                reason=f"target_type '{action_spec.target_type}'은 browser_tab이 아닙니다",
            )

        # action_type 추출 (intent에서 파싱 또는 raw_input prefix)
        action_type = self._extract_action_type(action_spec)
        if action_type not in _ACTION_POLICY:
            return DispatchResult(
                command_id="",
                action_spec=action_spec,
                queued=False,
                reason=f"지원되지 않는 action_type: '{action_type}'",
            )

        # 큐 등록
        self._expire_old_commands()
        command_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=_COMMAND_TTL_SECONDS)
        self._queue[command_id] = PendingCommand(
            command_id=command_id,
            action_type=action_type,
            action_spec_id=action_spec.action_id,
            expires_at=expires_at,
        )

        return DispatchResult(
            command_id=command_id,
            action_spec=action_spec,
            queued=True,
            reason=f"명령 큐 등록 완료 (TTL {_COMMAND_TTL_SECONDS}s)",
        )

    def pop_next_command(self) -> Optional[PendingCommand]:
        """
        Extension 폴링 엔드포인트 (GET /api/v1/browser/queue/next) 에서 호출.
        가장 오래된 미만료 명령을 _queue에서 _in_flight로 이동합니다.
        H-04 Fix: 즉시 삭제(pop) 대신 in_flight 보존 — ACK(receive_result) 후 제거.
        """
        self._expire_old_commands()
        if not self._queue:
            return None
        # 가장 먼저 등록된 명령 반환 (FIFO)
        command_id = next(iter(self._queue))
        cmd = self._queue.pop(command_id)
        # H-04 Fix: _in_flight에 보존 (Extension result ACK 전까지)
        self._in_flight[command_id] = cmd
        return cmd

    def ack_command(self, command_id: str) -> bool:
        """
        Extension result 수신 완료 후 in_flight에서 명령 제거 (ACK).
        H-04 Fix: receive_result() 성공 시 호출되어야 함.
        반환: True = 정상 ACK, False = 이미 만료/없음
        """
        return self._in_flight.pop(command_id, None) is not None

    # ──────────────────── 수신 경로 ───────────────────────────────

    def receive_result(self, result: BrowserResult) -> ReceiveResult:
        """
        Extension이 DOM 추출 후 POST /api/v1/browser/result 로 전송한 데이터 처리.

        처리 단계:
        1. PromptInjectionShield 스캔
        2. 저장 (Archive — V1은 AuditLedger 기록으로 대체)
        """
        scan = self._shield.scan(result.raw_content)
        if scan.injection_detected:
            # H-04 Fix: 차단 시에도 in_flight ACK — 재전송 무의미 (악성 콘텐츠)
            self.ack_command(result.command_id)
            return ReceiveResult(
                success=False,
                blocked=True,
                block_reason=f"Prompt Injection 감지: {scan.matched_patterns}",
                injection_risk=True,
            )

        # H-04 Fix: 정상 수신 완료 → in_flight ACK (명령 제거)
        self.ack_command(result.command_id)
        # V1: 저장은 AuditLedger/Archive 연동으로 확장 예정
        # 현재는 처리 성공으로 반환 (실제 저장은 browser_router.py에서 호출)
        return ReceiveResult(
            success=True,
            blocked=False,
            stored_content_length=len(result.raw_content),
        )

    def receive_push(self, payload: "BrowserPushPayload") -> "BrowserPushResult":
        """
        Extension 팝업 직접 푸시 경로 (Guard 미거침).
        ActionSpec 생성 + Shield 스캔 후 반환.
        Extension 팝업 → 백엔드 직접 POST /api/v1/browser/collect 경로.
        """
        if payload.action_type not in _ACTION_POLICY:
            return BrowserPushResult(
                action_spec=None,
                blocked=True,
                block_reason=f"미지원 action_type: '{payload.action_type}'",
            )

        scan = self._shield.scan(payload.raw_content)
        if scan.injection_detected:
            return BrowserPushResult(
                action_spec=None,
                blocked=True,
                block_reason=f"Prompt Injection 감지: {scan.matched_patterns}",
                injection_risk=True,
            )

        risk_level, requires_approval = _ACTION_POLICY[payload.action_type]
        intent = self._build_intent(payload.action_type, payload.title, payload.url)

        spec = ActionSpec(
            source=ActionSource.extension,
            raw_input=f"{payload.action_type}: {payload.url}",
            intent=intent,
            target_type=TargetType.browser_tab,
            target_ref=payload.url,
            risk_level=risk_level,
            requires_approval=requires_approval,
            preview_required=requires_approval,
        )
        return BrowserPushResult(action_spec=spec, blocked=False)

    # ──────────────────── 내부 헬퍼 ──────────────────────────────

    def _expire_old_commands(self) -> None:
        """TTL 초과 명령 제거 (_queue + _in_flight 모두)."""
        now = datetime.now(timezone.utc)
        expired_q = [cid for cid, cmd in self._queue.items() if cmd.expires_at < now]
        for cid in expired_q:
            del self._queue[cid]
        # H-04 Fix: in_flight TTL도 함께 만료 처리
        expired_if = [cid for cid, cmd in self._in_flight.items() if cmd.expires_at < now]
        for cid in expired_if:
            del self._in_flight[cid]

    @staticmethod
    def _extract_action_type(spec: ActionSpec) -> str:
        """ActionSpec.raw_input 또는 intent에서 action_type 추출."""
        raw = spec.raw_input.lower()
        if raw.startswith("save_tab:") or "탭 저장" in raw or "save" in raw:
            return "save_tab"
        if "summarize:" in raw or "요약" in raw:
            return "summarize"
        if "collect:" in raw or "수집" in raw:
            return "collect"
        return "save_tab"  # 기본값

    @staticmethod
    def _build_intent(action_type: str, title: str, url: str) -> str:
        t = (title or url)[:60]
        return {
            "save_tab":  f"현재 탭 저장: {t}",
            "summarize": f"페이지 요약: {t}",
            "collect":   f"브라우저 자료 수집: {t}",
        }.get(action_type, f"{action_type}: {t}")


# ─── 직접 푸시 타입 (Extension 팝업 경로) ────────────────────────

@dataclass
class BrowserPushPayload:
    """Extension 팝업 → POST /api/v1/browser/collect 직접 전송 페이로드."""
    action_type: str
    url: str
    title: str
    raw_content: str
    meta_description: str = ""
    word_count: int = 0


@dataclass
class BrowserPushResult:
    """receive_push() 반환값."""
    action_spec: Optional[ActionSpec]
    blocked: bool
    block_reason: str = ""
    injection_risk: bool = False
