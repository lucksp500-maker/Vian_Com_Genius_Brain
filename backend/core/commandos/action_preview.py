"""
Action Preview Engine — WO-003
ActionSpec → 사용자가 볼 수 있는 풀 Preview 데이터 직렬화.
대상 파일/URL/변경내용/위험도/실행 단계 표시.
"""
from __future__ import annotations

from backend.core.commandos.action_spec import ActionSpec, RiskLevel, TargetType


_RISK_DISPLAY = {
    RiskLevel.none.value: {"label": "안전", "color": "success", "icon": "check_circle"},
    RiskLevel.low.value: {"label": "낮음", "color": "info", "icon": "info"},
    RiskLevel.medium.value: {"label": "중간", "color": "warning", "icon": "warning"},
    RiskLevel.high.value: {"label": "높음 — 승인 필요", "color": "error", "icon": "dangerous"},
}

_TARGET_DISPLAY = {
    TargetType.file.value: "파일",
    TargetType.url.value: "URL / 웹 주소",
    TargetType.browser_tab.value: "현재 브라우저 탭",
    TargetType.text.value: "선택된 텍스트",
    TargetType.system.value: "시스템",
    TargetType.unknown.value: "알 수 없음",
}


def _build_execution_steps(spec: ActionSpec) -> list[dict]:
    """위험도와 target_type에 따른 실행 단계 목록 생성."""
    base_steps = [
        {"step": 1, "label": "Intent 파싱", "status": "completed", "description": f"AI 분류: {spec.intent}"},
        {"step": 2, "label": "Guard 판정", "status": "completed",
         "description": f"결과: {spec.guard_result or 'pending'} — {spec.guard_reason or ''}"},
    ]

    if spec.requires_approval:
        base_steps.append({
            "step": 3, "label": "사용자 승인 대기", "status": "pending",
            "description": "Approve and Execute 버튼을 누르면 진행됩니다"
        })
        next_step = 4
    else:
        next_step = 3

    if spec.target_type == TargetType.browser_tab.value:
        base_steps.append({
            "step": next_step, "label": "브라우저 컨텍스트 수집",
            "status": "pending", "description": "현재 탭 DOM 및 메타데이터 수집"
        })
    elif spec.target_type == TargetType.file.value:
        base_steps.append({
            "step": next_step, "label": "파일 접근 준비",
            "status": "pending", "description": "대상 파일 경로 확인 및 읽기 권한 검증"
        })

    base_steps.append({
        "step": next_step + 1, "label": "Audit 기록",
        "status": "pending", "description": "실행 결과를 Audit Ledger에 저장"
    })

    return base_steps


def _build_safety_warnings(spec: ActionSpec) -> list[dict]:
    """위험도에 따른 안전 경고 목록 생성."""
    warnings: list[dict] = []

    if spec.risk_level == RiskLevel.high.value:
        warnings.append({
            "level": "critical",
            "icon": "warning",
            "title": "고위험 작업",
            "detail": "이 작업은 되돌리기 어렵습니다. 반드시 내용을 확인 후 승인하세요.",
        })

    if spec.target_type in (TargetType.url.value,):
        warnings.append({
            "level": "warning",
            "icon": "language",
            "title": "외부 통신 포함",
            "detail": "이 작업은 외부 서버와 통신합니다. 데이터 전송 범위를 확인하세요.",
        })

    if spec.target_type == TargetType.browser_tab.value and spec.risk_level == RiskLevel.high.value:
        warnings.append({
            "level": "warning",
            "icon": "tab",
            "title": "브라우저 조작 포함",
            "detail": "현재 탭의 폼 또는 콘텐츠를 수정할 수 있습니다.",
        })

    return warnings


def build_preview(spec: ActionSpec) -> dict:
    """
    ActionSpec → Web App ActionPreviewPanel이 소비하는 preview dict.

    필드:
    - action_id
    - intent (자연어 의도 설명)
    - target_display (사람이 읽기 좋은 대상 유형)
    - target_ref (구체적 파일/URL, 없으면 null)
    - risk_display (위험도 라벨/색상/아이콘)
    - requires_approval
    - guard_result / guard_reason
    - execution_steps (단계별 실행 계획)
    - safety_warnings (경고 목록)
    - raw_input (원본 자연어 입력)
    """
    return {
        "action_id": spec.action_id,
        "intent": spec.intent or spec.raw_input,
        "raw_input": spec.raw_input,
        "target_display": _TARGET_DISPLAY.get(spec.target_type, "알 수 없음"),
        "target_ref": spec.target_ref,
        "risk_display": _RISK_DISPLAY.get(spec.risk_level, _RISK_DISPLAY[RiskLevel.medium.value]),
        "requires_approval": spec.requires_approval,
        "guard_result": spec.guard_result,
        "guard_reason": spec.guard_reason,
        "execution_state": spec.execution_state,
        "execution_steps": _build_execution_steps(spec),
        "safety_warnings": _build_safety_warnings(spec),
    }
