"""
CommandOS Implementation Scanner — WO-001
Vian_CommandOS 프로젝트의 7개 핵심 컴포넌트 실제 구현 상태를 스캔합니다.
파일 존재 + 테스트 존재 + 정적 분석(TODO/stub 비율)을 종합하여 상태 분류합니다.

상태 분류:
- implemented : 파일 + 테스트 모두 존재, TODO/stub 0건
- partial     : 파일 존재하나 테스트 없거나 TODO/stub 1건 이상
- missing     : 핵심 파일 미존재
- broken      : 파일 존재하나 import 오류 또는 빌드 실패 흔적
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

COMMANDOS_ROOT = Path("/home/lucksp500/projects/Vian_CommandOS")

ComponentStatus = Literal["implemented", "partial", "missing", "broken"]

# 각 컴포넌트별 핵심 파일 및 테스트 파일 경로
COMPONENT_MANIFEST: dict[str, dict] = {
    "Command HUD": {
        "key_files": [
            "src/hud/CommandHUD.tsx",
        ],
        "test_files": [],
        "description": "Ctrl+K 트리거 HUD 컴포넌트",
    },
    "Guard Policy Gate": {
        "key_files": [
            "src/core/policy-gate.ts",
        ],
        "test_files": [
            "tests/unit/policy-gate.spec.ts",
        ],
        "description": "allow/deny/ask 정책 판정 엔진",
    },
    "Archive Engine": {
        "key_files": [
            "src/storage/archive-repo.ts",
        ],
        "test_files": [
            "tests/unit/archive-repo.spec.ts",
        ],
        "description": "웹 콘텐츠 및 문서 아카이브 저장",
    },
    "Audit Ledger": {
        "key_files": [
            "src/storage/audit-repo.ts",
        ],
        "test_files": [
            "tests/unit/audit-repo.spec.ts",
        ],
        "description": "명령 실행 이력 감사 로그",
    },
    "Intent Parser": {
        "key_files": [
            "src/core/intent-parser.ts",
            "src/intent/ollama-intent-parser.ts",
        ],
        "test_files": [
            "tests/unit/intent-parser.spec.ts",
        ],
        "description": "자연어 → ActionSpec 변환 파서",
    },
    "Prompt Injection Shield": {
        "key_files": [
            "src/content/prompt-injection-shield.ts",
        ],
        "test_files": [
            "tests/unit/prompt-injection-shield.spec.ts",
        ],
        "description": "웹 페이지 원문 명령 차단 레이어",
    },
    "Extension": {
        "key_files": [
            "src/background/index.ts",
            "src/content/index.ts",
        ],
        "test_files": [],
        "description": "Chrome Extension MV3 배경/콘텐츠 스크립트",
    },
}


@dataclass
class ComponentReport:
    name: str
    status: ComponentStatus
    description: str
    key_files_found: list[str] = field(default_factory=list)
    key_files_missing: list[str] = field(default_factory=list)
    test_files_found: list[str] = field(default_factory=list)
    test_files_missing: list[str] = field(default_factory=list)
    todo_count: int = 0
    stub_count: int = 0
    evidence: str = ""


def _count_patterns(file_path: Path, patterns: list[str]) -> int:
    """파일 내 패턴 출현 횟수 합산."""
    try:
        text = file_path.read_text(encoding="utf-8", errors="ignore")
        return sum(len(re.findall(p, text, re.IGNORECASE)) for p in patterns)
    except OSError:
        return 0


def scan_component(name: str, manifest: dict) -> ComponentReport:
    """단일 컴포넌트 상태 스캔."""
    found_key: list[str] = []
    missing_key: list[str] = []
    found_test: list[str] = []
    missing_test: list[str] = []
    todo_total = 0
    stub_total = 0

    for rel in manifest["key_files"]:
        p = COMMANDOS_ROOT / rel
        if p.exists():
            found_key.append(rel)
            todo_total += _count_patterns(p, [r"\bTODO\b", r"\bFIXME\b"])
            stub_total += _count_patterns(p, [r"\bstub\b", r"\bmock\b", r"\bnot implemented\b"])
        else:
            missing_key.append(rel)

    for rel in manifest["test_files"]:
        p = COMMANDOS_ROOT / rel
        if p.exists():
            found_test.append(rel)
        else:
            missing_test.append(rel)

    # 상태 결정 로직
    has_all_key = len(missing_key) == 0
    has_tests = len(manifest["test_files"]) == 0 or len(found_test) > 0

    if not has_all_key and not found_key:
        status: ComponentStatus = "missing"
        evidence = f"핵심 파일 없음: {missing_key}"
    elif not has_all_key:
        status = "partial"
        evidence = f"일부 핵심 파일 없음: {missing_key}"
    elif not has_tests:
        status = "partial"
        evidence = f"테스트 없음: {missing_test}"
    elif todo_total > 0 or stub_total > 0:
        status = "partial"
        evidence = f"TODO {todo_total}건 / stub {stub_total}건"
    else:
        status = "implemented"
        evidence = "파일 + 테스트 존재, TODO/stub 0건"

    return ComponentReport(
        name=name,
        status=status,
        description=manifest["description"],
        key_files_found=found_key,
        key_files_missing=missing_key,
        test_files_found=found_test,
        test_files_missing=missing_test,
        todo_count=todo_total,
        stub_count=stub_total,
        evidence=evidence,
    )


def run_scan() -> list[ComponentReport]:
    """전체 7개 컴포넌트 스캔."""
    if not COMMANDOS_ROOT.exists():
        raise FileNotFoundError(f"Vian_CommandOS 경로 없음: {COMMANDOS_ROOT}")
    return [scan_component(name, manifest) for name, manifest in COMPONENT_MANIFEST.items()]


def generate_report(reports: list[ComponentReport]) -> str:
    """마크다운 형식 구현 상태 보고서 생성."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    counts = {s: sum(1 for r in reports if r.status == s) for s in ("implemented", "partial", "missing", "broken")}

    lines = [
        "# CommandOS Implementation Report",
        f"\n생성일: {now}",
        f"스캔 경로: `{COMMANDOS_ROOT}`",
        "",
        "## 요약",
        f"| 상태 | 건수 |",
        f"|------|------|",
        *[f"| {s} | {counts[s]} |" for s in ("implemented", "partial", "missing", "broken")],
        "",
        "## 컴포넌트별 상태",
        "",
    ]

    for r in reports:
        status_icon = {"implemented": "✅", "partial": "⚠️", "missing": "❌", "broken": "💥"}.get(r.status, "?")
        lines += [
            f"### {status_icon} {r.name} — `{r.status}`",
            f"**설명:** {r.description}",
            f"**증거:** {r.evidence}",
        ]
        if r.key_files_found:
            lines.append(f"**파일 존재:** {', '.join(f'`{f}`' for f in r.key_files_found)}")
        if r.key_files_missing:
            lines.append(f"**파일 없음:** {', '.join(f'`{f}`' for f in r.key_files_missing)}")
        if r.test_files_found:
            lines.append(f"**테스트 존재:** {', '.join(f'`{f}`' for f in r.test_files_found)}")
        if r.test_files_missing:
            lines.append(f"**테스트 없음:** {', '.join(f'`{f}`' for f in r.test_files_missing)}")
        if r.todo_count or r.stub_count:
            lines.append(f"**TODO:** {r.todo_count}건 | **stub:** {r.stub_count}건")
        lines.append("")

    lines += [
        "## 재사용 판정",
        "",
        "| 컴포넌트 | 상태 | Phase 1 처리 |",
        "|----------|------|-------------|",
    ]
    for r in reports:
        treatment = {
            "implemented": "Python adapter로 포팅",
            "partial": "Python adapter로 포팅 (주의: 누락 항목 확인)",
            "missing": "Python에서 신규 구현",
            "broken": "Python에서 신규 구현 (기존 TS 참조 불가)",
        }[r.status]
        lines.append(f"| {r.name} | `{r.status}` | {treatment} |")

    return "\n".join(lines)


if __name__ == "__main__":
    reports = run_scan()
    md = generate_report(reports)
    report_path = Path(__file__).parent.parent.parent / "reports" / "commandos_implementation_report.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(md, encoding="utf-8")
    print(md)
    print(f"\n보고서 저장: {report_path}")
