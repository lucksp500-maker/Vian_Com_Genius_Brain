"""
WO-001 — implementation_scanner.py 테스트
"""
import pytest
from pathlib import Path

from backend.core.commandos.implementation_scanner import (
    COMPONENT_MANIFEST,
    ComponentReport,
    ComponentStatus,
    run_scan,
    scan_component,
    generate_report,
    COMMANDOS_ROOT,
)


def test_commandos_root_exists():
    """Vian_CommandOS 경로 존재 확인."""
    assert COMMANDOS_ROOT.exists(), f"Vian_CommandOS 경로 없음: {COMMANDOS_ROOT}"


def test_component_manifest_has_7_components():
    """7개 컴포넌트 모두 정의됐는지 확인."""
    expected = {
        "Command HUD",
        "Guard Policy Gate",
        "Archive Engine",
        "Audit Ledger",
        "Intent Parser",
        "Prompt Injection Shield",
        "Extension",
    }
    assert set(COMPONENT_MANIFEST.keys()) == expected


def test_scan_returns_7_reports():
    """스캔 결과가 정확히 7개 ComponentReport인지 확인."""
    reports = run_scan()
    assert len(reports) == 7


def test_all_reports_have_valid_status():
    """모든 리포트 상태가 유효한 값인지 확인."""
    valid: set[ComponentStatus] = {"implemented", "partial", "missing", "broken"}
    for r in run_scan():
        assert r.status in valid, f"{r.name}: 유효하지 않은 상태 '{r.status}'"


def test_guard_policy_gate_implemented():
    """Guard Policy Gate는 implemented 또는 partial — 파일이 존재해야 함."""
    reports = run_scan()
    guard_report = next(r for r in reports if r.name == "Guard Policy Gate")
    assert guard_report.status in ("implemented", "partial"), (
        f"Guard Policy Gate 상태 예상 implemented/partial, 실제: {guard_report.status}"
    )
    assert len(guard_report.key_files_found) > 0, "Guard Policy Gate 핵심 파일 없음"


def test_intent_parser_implemented():
    """Intent Parser는 implemented 또는 partial."""
    reports = run_scan()
    parser_report = next(r for r in reports if r.name == "Intent Parser")
    assert parser_report.status in ("implemented", "partial"), (
        f"Intent Parser 상태 예상 implemented/partial, 실제: {parser_report.status}"
    )


def test_prompt_injection_shield_implemented():
    """Prompt Injection Shield는 implemented 또는 partial."""
    reports = run_scan()
    shield_report = next(r for r in reports if r.name == "Prompt Injection Shield")
    assert shield_report.status in ("implemented", "partial"), (
        f"Prompt Injection Shield 상태: {shield_report.status}"
    )


def test_generate_report_contains_all_components():
    """보고서 마크다운에 7개 컴포넌트 이름 모두 포함되는지 확인."""
    reports = run_scan()
    md = generate_report(reports)
    for name in COMPONENT_MANIFEST:
        assert name in md, f"보고서에 '{name}' 없음"


def test_generate_report_contains_status_summary():
    """보고서 마크다운에 요약 테이블 포함 확인."""
    reports = run_scan()
    md = generate_report(reports)
    assert "implemented" in md
    assert "partial" in md or "missing" in md or "broken" in md  # 어떤 상태든 하나는 있어야


def test_scan_component_missing_status():
    """존재하지 않는 파일이 명시된 컴포넌트는 missing 또는 partial 반환."""
    fake_manifest = {
        "key_files": ["src/nonexistent_file_xyz.ts"],
        "test_files": [],
        "description": "테스트용 가짜 컴포넌트",
    }
    report = scan_component("FakeComponent", fake_manifest)
    assert report.status in ("missing", "partial")
    assert any("nonexistent_file_xyz.ts" in f for f in report.key_files_missing)
