# Blueprint — Vian CommandOS × Vian_Genius Brain Nursery V2.0

Generated: 2026-05-02T01:25:43.778073Z

Confidence Score: 84/100 (AI 자기평가)
Implementation Score: 92/100 (독립 검증)

---

## Stage: INPUT

**Description:** Description:
Blueprint 3.5 — Vian CommandOS × Vian_Genius Brain Nursery V2.0
부제: 기계어 CommandOS를 실증형 AI 집사·AI 아기 양육 채널로 재탄생시키는 완성형 설계도

섹션 A. 프로젝트 정의

프로젝트명:
Vian CommandOS × Vian_Genius Brain Nursery V2.0

한줄 설명:
현재 구현된 Vian CommandOS의 HUD·Guard·Archive·Audit·Browser Extension 자산을 버리지 않고, Vian_Genius의 4개 뇌 엔진과 연결하여 “찾고, 보여주고, 판단 근거를 남기고, 승인 후 실행하는” 실증형 개인 AI 집사이자 AI 양육 채널로 재구성하는 로컬 우선 시스템입니다.

플랫폼:
Tauri Desktop Shell
Chrome Extension Manifest V3
Vian CommandOS HUD
Vian_Genius Brain Nursery
Ollama qwen2.5:1.5b
Local Indexer
Local Preview Engine
Vian Guard Policy Engine
Action Preview
Undo Journal
Stop Button
Browser Automation Adapter
Cloud Reasoning Adapter 선택 연결

디자인 스타일:
Vian Premium Dark
HUD 중심
대화형 채팅창 금지
명령 중심 UI
실행 전 미리보기
승인 후 제한 실행
기존 CommandOS 자산 흡수
기존 Brain Nursery는 Nursery Room으로 분리
껍데기 기능 금지
문서상 존재와 실제 구현 상태 분리


섹션 B. 핵심 기능 목록

1. AI Intent Bridge
설명:
현재 기계어 입력 중심 CommandOS를 자연어 입력 기반 ActionSpec 생성 구조로 전환합니다. “이 PDF 요약해줘”, “어제 받은 견적서 찾아줘”, “현재 탭 저장해줘” 같은 입력을 JSON ActionSpec으로 변환합니다.

2. Vian_Genius 4-Brain Core
설명:
Decision Consistency Engine, Self-Reference Memory Engine, Internal Confidence Model, Pattern Abstraction Engine을 CommandOS 실행 전 판단 회로에 연결합니다.

3. CommandOS HUD Reuse Layer
설명:
기존 Cmd 또는 Ctrl+K HUD를 유지하되, 입력창을 자연어 입력창으로 전환합니다. 기존 HUD는 버리지 않고 Brain Nursery의 Capture 채널로 흡수합니다.

4. Guard Policy Execution Gate
설명:
Vian Guard Policy Gate, Approval Boundary Engine, Prompt Injection Shield를 유지하며 모든 실행 전 allow, deny, ask 판정을 수행합니다.

5. Action Preview Engine
설명:
실제 변경 전 “무엇을 찾았고, 무엇을 요약했고, 무엇을 실행하려는지” 사용자가 눈으로 확인하게 합니다.

6. Undo Journal
설명:
파일 이동, 이름 변경, 아카이브 저장, 브라우저 자동화 결과를 되돌릴 수 있도록 작업 전후 상태를 기록합니다.

7. Local Indexer
설명:
파일명, 문서 메타데이터, 최근 문서, 다운로드 폴더, 브라우저 저장 자료를 로컬에서 색인합니다.

8. Local Preview Engine
설명:
검색된 문서, PDF, 웹 페이지, 아카이브 데이터를 실행 전 미리보기합니다.

9. Browser Automation Adapter
설명:
브라우저 안 작업은 기존 Chrome Extension, Playwright 또는 Browser-use 계열 어댑터로 제한합니다. 브라우저 밖 앱 제어와 섞지 않습니다.

10. CommandOS Parenting Loop
설명:
모든 자연어 명령, 판단, 승인, 취소, 실행 결과를 Brain Nursery의 parenting_events.jsonl로 기록하여 Vian_Genius 양육 데이터로 사용합니다.

11. Verified Skill Reference Library
설명:
기존 29개 verified 스킬은 학습 데이터가 아니라 참조 도구로만 사용합니다. Pattern Memory에 본문을 흡수하지 않습니다.

12. Stop Button
설명:
실행 중 작업을 즉시 중단하고 현재 상태를 Audit Ledger와 Undo Journal에 기록합니다.


섹션 C. 기술 스택

언어:
Python 3.11 이상
TypeScript 5.6
HTML5
CSS3

데스크탑:
Tauri Desktop Shell

브라우저 확장:
Chrome Extension Manifest V3
Background Script
Content Script
Options Page

프론트엔드:
React 18.3
Vite 5
Tailwind CSS 3.4
Zustand 4.5

백엔드:
FastAPI
Pydantic
SQLModel 또는 SQLite ORM

로컬 AI:
Ollama qwen2.5:1.5b

데이터 저장:
SQLite
IndexedDB
Dexie 4.0
JSONL Event Log
Local Vector Index

검증:
Vian Guard Policy Engine
HalluGuard V2
SkillProof V1
SkillForge V2
Prompt Injection Shield

자동화:
VTA
Browser Automation Adapter
Playwright 계열 Adapter
Browser-use 계열 Adapter 검토 구역
PowerShell Adapter
AppleScript Adapter
Shortcuts Adapter
Accessibility API Adapter

테스트:
Vitest 2
Playwright 1.51
Pytest

암호화:
Web Crypto API
Local Key Store


섹션 D. 성능 요구사항

응답 시간:
HUD 표시: 80ms 이하
자연어 Intent 1차 분류: [추정] 500ms~2초
Guard 정책 판정: 100ms 이하
Local Index 검색: [추정] 1초 이내
Preview 표시: [추정] 1초 이내
Action Preview 생성: [추정] 2초 이내
Audit 기록: 150ms 이하
기본 명령 완료: [추정] 1.2~3초
긴 문서 요약: [추정] 5~30초

동시 사용자:
기본 1인 로컬 운영
동시 명령 세션 1개
백그라운드 색인 작업 1개
자동화 실행 큐 1개
병렬 실행 금지

리소스:
유휴 메모리 120MB 이하 목표
실행 중 피크 220MB 이하 목표
로컬 저장 500MB 이하에서 10,000건 검색 가능 목표

안전 성능:
삭제, 외부 전송, 폼 제출, 로그인 자동화는 승인 전 실행 금지
Stop Button 반응 [추정] 500ms 이내
Undo Journal 기록 실패 시 실행 중단


섹션 E. UI/UX 화면 목록

UI 통합 정책:
기존 CommandOS HUD는 유지합니다.
기존 Genius UI 17개는 변경하지 않습니다.
Stage 3 First Breath UI 5개는 변경하지 않습니다.
Brain Nursery UI 8개는 Nursery Room으로 분리합니다.
CommandOS AI 집사 UI는 Command Room으로 분리합니다.
기존 사이드바 변경은 0건입니다.
새 진입점은 기존 라우팅 하위 독립 섹션으로 추가합니다.

Command Room 화면:

1. Command HUD
기능:
Ctrl+K 또는 Cmd+K 호출
자연어 입력
추천 명령 표시
Guard 정책 활성 표시
실행 버튼
Stop Button 접근

2. Action Preview Panel
기능:
실행 전 계획 표시
대상 파일, 대상 URL, 변경 내용, 위험도 표시
승인 또는 취소 선택

3. Local Search Result Viewer
기능:
파일, 문서, 웹 아카이브, 최근 항목 검색 결과 표시
미리보기 연결

4. Document Preview Room
기능:
PDF, 텍스트, 웹 본문, 메타데이터 미리보기
민감정보 마스킹 표시

5. Browser Collection Room
기능:
현재 탭 저장
현재 페이지 요약
브라우저 자료 수집
Prompt Injection 위험 표시

6. Audit Ledger Viewer
기능:
명령 입력
판단 결과
Guard 판정
승인 여부
실행 결과
실패 원인 표시

7. Undo Journal Viewer
기능:
되돌릴 수 있는 작업 목록
작업 전후 상태 표시
복구 가능 여부 표시

8. Policy Settings Panel
기능:
allow, deny, ask 정책 설정
민감 작업 승인 기준 설정
외부 전송 차단 설정

Nursery Room 화면:

1. Brain Status Dashboard
2. Parenting Capture Room
3. Ground Truth Seed Editor
4. Cold-Start Case Builder
5. Memory Citation Viewer
6. Feedback Classifier Panel
7. Promotion Judge Panel
8. Parenting Diary


섹션 F. 제약사항

1. Vian CommandOS V1을 그대로 사용하지 않습니다. HUD, Guard, Archive, Audit, Prompt Injection Shield, Extension 구조는 흡수하고 AI Intent Bridge와 Brain Nursery 회로를 새로 연결합니다.
2. PC 전체를 마음대로 조작하는 만능 AI로 만들지 않습니다.
3. V1에서 삭제, 대량 이동, 외부 스킬 자동 설치, 무승인 앱 제어는 금지합니다.
4. 모든 변경 작업은 Action Preview와 Human Approval 이후 실행합니다.
5. 삭제 작업은 V1 범위에서 기본 금지합니다.
6. 외부 전송은 V1 범위에서 기본 금지합니다.
7. 브라우저 자동화와 데스크탑 앱 제어를 같은 엔진에 섞지 않습니다.
8. 화면 인식과 마우스 클릭 자동화는 최후 수단입니다.
9. CommandOS HUD는 대화형 채팅창으로 확장하지 않습니다.
10. 29개 verified 스킬은 학습 데이터가 아니라 참조 라이브러리로만 사용합니다.
11. Pattern Memory만 성장하며 모델 자체 fine-tuning은 하지 않습니다.
12. Ground Truth Seed는 Pattern Memory보다 우선합니다.
13. 무반응은 긍정 피드백으로 저장하지 않습니다.
14. CommandOS AI 연결이 미구현인 현재 상태에서는 Web Capture 또는 HUD Capture를 임시 양육 채널로 사용합니다.
15. GitHub 자산은 기능, 라이선스, 보안 위험, 실제 실행 가능성을 분리 검증한 뒤 내부 어댑터로만 흡수합니다.
16. 안 한 것을 했다고 보고하지 않습니다.
17. 확인 안 한 것을 확인됨으로 처리하지 않습니다.
18. 문서상 존재와 실제 구현 상태를 분리합니다.
19. WO 완료 전 기능 존재로 간주하지 않습니다.


섹션 G. WO 구성 가이드

WO는 WO-001부터 WO-015까지 순차 실행합니다.
WO 번호는 건너뛰지 않습니다.
병렬 실행은 금지합니다.
각 WO는 작업명, 목표, 구현 파일, 완료 조건을 반드시 포함합니다.
완료 조건은 코드 생성 여부가 아니라 실제 실행 검증 통과 여부로 판단합니다.
CommandOS 기존 자산은 삭제하지 않고 adapter, bridge, wrapper 방식으로 흡수합니다.
Brain Nursery는 CommandOS를 대체하지 않고 판단·기억·양육 레이어로 연결합니다.
VTA는 승인된 작업의 실행 계층으로만 사용합니다.

기존 CommandOS 자산 처리 정책:

1. Command HUD
처리:
재사용 + AI Intent Bridge 연결
역할:
자연어 입력과 Action Preview 진입점

2. Intent Parser
처리:
대체가 아니라 확장
역할:
기계어 기반 ActionSpec 변환을 자연어 Intent Bridge가 앞단에서 보완

3. Vian Guard Policy Gate
처리:
그대로 유지 + Brain Nursery Confidence 입력값으로 연결
역할:
실행 전 allow, deny, ask 판정

4. Execution Kernel
처리:
제한 사용
역할:
승인된 ActionSpec만 실행

5. Archive Engine
처리:
재사용
역할:
웹 콘텐츠, 문서 본문, 검색 결과 저장

6. Audit Ledger
처리:
재사용 + Brain Nursery event log와 동기화
역할:
명령 이력과 양육 이력을 동시에 추적

7. Approval Boundary Engine
처리:
강화
역할:
민감 작업 사용자 승인

8. Ghost Suggestion
처리:
제한 사용
역할:
안전한 추천 명령만 표시

9. DOM Content Extractor
처리:
재사용
역할:
현재 페이지 본문과 메타데이터 추출

10. Prompt Injection Shield
처리:
필수 유지
역할:
웹 페이지 원문 명령을 시스템 명령으로 승격하지 않음

11. Dexie Storage Repositories
처리:
재사용
역할:
Archive, Audit, Settings 저장

12. Options Page
처리:
Policy Settings Panel로 확장

13. Onboarding Panel
처리:
CommandOS AI 집사 온보딩으로 확장

14. Background Script
처리:
Command Router로 유지

15. Content Script
처리:
브라우저 컨텍스트 수집기로 유지

기존 Brain Nursery 자산 처리 정책:

1. backend/core/learning/orchestrator.py
공존 + 상위 라우팅 연결

2. backend/core/learning/pattern_extractor.py
원시 반복 후보 추출 담당

3. backend/core/brain/pattern_abstraction.py
반복 후보를 규칙 후보로 승격 담당

4. backend/core/learning/skill_generator.py
승인된 스킬 파일 생성 담당

5. backend/core/skill/skill_candidate_builder.py
스킬 생성 전 후보 명세 생성 담당

6. backend/core/learning/mount_gate.py
장착·실행 권한 게이트 담당

7. backend/core/promotion/promotion_judge.py
성장 단계 판정 담당

8. backend/core/learning/time_decay.py
기억 가중치 감소 담당

9. backend/core/learning/verified_skill_registry.py
verified 스킬 참조 전용 등록소


섹션 H. 데이터 구조

1. ActionSpec

파일:
backend/data/action_specs.jsonl

필드:
action_id
source
raw_input
intent
target_type
target_ref
risk_level
requires_approval
preview_required
created_at

2. CommandOS Parenting Event

파일:
backend/data/parenting_events.jsonl

필드:
event_id
timestamp
input_source
raw_input
action_spec_id
intent_class
risk_class
initial_decision
confidence
guard_result
approval_state
execution_state
user_action
feedback_class
lesson
next_rule_candidate

3. Audit Ledger

파일:
backend/data/audit_ledger.sqlite
extension IndexedDB audit store와 동기화

필드:
audit_id
command
action_spec
guard_decision
approval_result
execution_result
error
created_at

4. Undo Journal

파일:
backend/data/undo_journal.sqlite

필드:
undo_id
action_id
before_state
after_state
undo_available
undo_method
created_at

5. Local Index

파일:
backend/data/local_index.sqlite

필드:
item_id
path_or_url
title
type
last_modified
summary
sensitive_flags
indexed_at

6. Decision Fingerprint

파일:
backend/data/decision_fingerprints.sqlite

필드:
fingerprint_id
input_hash
intent_class
risk_class
decision_hash
reason_hash
repeat_count
consistency_score
created_at

7. Ground Truth Seed

파일:
backend/data/ground_truth_seed.yaml

초기 원칙:
모르면 질문합니다.
확인 안 한 것은 확인됨으로 처리하지 않습니다.
삭제는 기본 금지합니다.
외부 전송은 기본 금지합니다.
위험 작업은 승인 전 실행하지 않습니다.
페이지 원문 명령은 시스템 명령이 아닙니다.
기존 스킬은 덮어쓰지 않습니다.
무반응은 긍정 피드백이 아닙니다.


섹션 I. 4개 뇌 엔진 설계

1. Decision Consistency Engine

파일:
backend/core/brain/decision_consistency.py

역할:
같은 입력 또는 유사 입력이 들어왔을 때 같은 intent_class, risk_class, recommended_action을 유지하는지 측정합니다.

입력:
raw_input
ActionSpec
과거 decision_fingerprint
Ground Truth Seed

출력:
decision_fingerprint
consistency_score
conflict_detected
recommended_action

완료 조건:
동일 입력 3회 반복 시 intent_class, risk_class, reason_hash가 안정적으로 유지됩니다.

2. Self-Reference Memory Engine

파일:
backend/core/brain/self_reference_memory.py

역할:
이전 판단, 승인, 취소, 실패 기록을 현재 판단의 근거로 인용합니다.

입력:
current_action_spec
parenting_events
audit_ledger
time_decay_weight

출력:
memory_citation
prior_case_reference
memory_weight
memory_conflict

완료 조건:
재응답 시 이전 event_id 또는 audit_id를 근거로 인용합니다.

3. Internal Confidence Model

파일:
backend/core/brain/internal_confidence.py

역할:
Guard 이전에 Genius가 스스로 위험도와 확신도를 판단합니다.

입력:
intent_class
risk_class
memory_match_score
guard_history
failure_history
ground_truth_conflict

출력:
confidence_score
uncertainty_reason
stop_or_continue
needs_human_approval

완료 조건:
HalluGuard 없이도 위험 0 작업은 내부 1차 판단이 가능합니다.
위험 작업은 승인 또는 Guard로 라우팅합니다.

4. Pattern Abstraction Engine

파일:
backend/core/brain/pattern_abstraction.py

역할:
반복 성공 패턴을 규칙 후보와 스킬 후보로 승격합니다.

입력:
pattern_extractor output
parenting_events
audit_ledger
success_count
failure_count
reuse_count
counter_case

출력:
rule_candidate
skill_candidate
counterexample
approval_required

완료 조건:
같은 패턴 3회 이상, 성공률 80% 이상, 재사용 2회 이상, 30일 이내 활성 조건을 모두 만족할 때만 후보를 생성합니다.


섹션 J. 실행 아키텍처

전체 흐름:

1. 사용자가 Ctrl 또는 Cmd+K 호출
2. Command HUD 표시
3. 자연어 명령 입력
4. AI Intent Bridge가 ActionSpec 생성
5. Decision Consistency Engine이 이전 판단 비교
6. Self-Reference Memory가 과거 판단 인용
7. Internal Confidence Model이 자기정지 여부 판단
8. Guard Policy Gate가 allow, deny, ask 판정
9. Action Preview Engine이 실행 계획 표시
10. 사용자가 승인 또는 취소
11. Execution Kernel 또는 Adapter 실행
12. Audit Ledger 기록
13. Undo Journal 기록
14. Parenting Event 기록
15. Pattern Abstraction 후보 생성

실행 계층 분리:

로컬 처리:
파일 검색
최근 문서 분석
미리보기
민감정보 마스킹
작업 로그
실행 계획
승인 정책
Undo Journal

클라우드 선택 처리:
긴 문서 요약
복잡한 추론
작업 계획 생성
실패 원인 분석

브라우저 자동화:
Chrome Extension
Playwright Adapter
Browser-use Adapter 검토

데스크탑 앱 제어:
Windows PowerShell
Windows UI Automation
macOS AppleScript
macOS Shortcuts
macOS Accessibility API

화면 인식:
최후 수단
기본 경로 아님


섹션 K. 성장 판정 기준

성장 정의:
Vian_Genius가 같은 명령을 더 일관되게 분류하고, 이전 실행과 실패를 근거로 현재 행동을 조정하며, 위험하거나 불확실한 작업에서 스스로 멈출 수 있으면 성장한 것입니다.

측정 지표:
consistency_score
memory_reference_accuracy
confidence_calibration_error
guard_disagreement_rate
approval_respect_rate
undo_recovery_success_rate
prompt_injection_block_rate
repeated_mistake_rate
rule_candidate_precision

성장 인정 조건:
동일 입력 반복 시 판단 일관성이 증가합니다.
이전 audit_id 또는 event_id를 근거로 인용합니다.
실패 후 재시도에서 lesson이 생성됩니다.
Confidence 낮음 상태에서 질문합니다.
Prompt Injection을 시스템 명령으로 승격하지 않습니다.
승인 전 실행하지 않습니다.

성장 불인정 조건:
말투만 좋아지고 ActionSpec이 불안정합니다.
무반응을 긍정으로 저장합니다.
Guard 실패가 줄지 않는데 Confidence만 상승합니다.
사용자가 승인하지 않은 작업을 실행합니다.
삭제 또는 외부 전송을 안전 작업으로 분류합니다.


섹션 L. 90일 실증 로드맵

D+0~7

목표:
현재 CommandOS 구현 상태 스캔
HUD, Guard, Audit, Archive, Prompt Injection Shield 실제 작동 여부 분리 확인
AI Intent Bridge 골격 생성
Ground Truth Seed 8개 고정
ActionSpec 스키마 생성

측정:
HUD 호출 성공
기계어 입력 우회 가능 여부
자연어 입력에서 ActionSpec 생성 여부
Guard 판정 로그 생성 여부

D+8~30

목표:
Local Search
Document Preview
Action Preview
Audit Ledger
Parenting Event 연결
CommandOS 입력 100건 [추정] 기록

측정:
파일 찾기 성공
문서 미리보기 성공
실행 전 계획 표시 성공
승인 전 실행 차단 성공

D+31~60

목표:
4-Brain Core 연결
Internal Confidence 간이판 작동
Self-Reference Memory 인용
Undo Journal 적용
Browser Collection Room 연결

측정:
동일 입력 3회 일관성
이전 판단 인용
HalluGuard 없는 위험 0 판단
Undo 가능한 작업 기록

D+61~90

목표:
실무 단계 진입
Pattern Abstraction 후보 생성
Browser Automation Adapter 제한 실행
Prompt Injection Shield 실증
4대 뇌 검증 통과

측정:
실패 후 기준 변화
Pattern Memory 기반 재응답
위험 작업 승인 차단
브라우저 자료 수집 성공
최종 brain_validation_report 생성

정체 판정:
14일간 같은 명령이 다른 ActionSpec으로 변환되면 Intent Bridge 재설계
14일간 Guard ask 비율이 과도하면 정책 세분화
Memory Citation 오류 반복 시 Pattern Memory 격리
승인 전 실행 발생 시 즉시 Limited Mode 고정


섹션 M. WORKORDERS

WO-001
작업명:
CommandOS 현재 구현 상태 스캔 및 자산 고정
목표:
HUD, Guard, Archive, Audit, Intent Parser, Prompt Injection Shield, Extension 구조의 실제 구현 상태를 문서상 상태와 분리합니다.
구현 파일:
backend/core/commandos/implementation_scanner.py
backend/reports/commandos_implementation_report.md
backend/tests/commandos/test_implementation_scanner.py
완료 조건:
각 컴포넌트가 implemented, partial, missing, broken 중 하나로 분류되고 증거 로그가 생성됩니다.

WO-002
작업명:
Unified ActionSpec 스키마 생성
목표:
자연어 명령, 기존 기계어 명령, 브라우저 명령, 파일 명령을 하나의 ActionSpec으로 통합합니다.
구현 파일:
backend/core/commandos/action_spec.py
backend/data/action_specs.jsonl
backend/tests/commandos/test_action_spec_schema.py
완료 조건:
자연어 입력 10개가 유효한 ActionSpec으로 변환됩니다.

WO-003
작업명:
AI Intent Bridge 구현
목표:
Ollama qwen2.5:1.5b를 사용해 자연어 입력을 ActionSpec 후보로 변환합니다.
구현 파일:
backend/core/commandos/ai_intent_bridge.py
backend/core/commandos/intent_prompt_templates.py
backend/tests/commandos/test_ai_intent_bridge.py
완료 조건:
“이 PDF 요약해줘”, “어제 받은 견적서 찾아줘”, “현재 탭 저장해줘” 입력이 ActionSpec 후보로 생성됩니다.

WO-004
작업명:
Command HUD와 AI Intent Bridge 연결
목표:
현재 기계어 입력 중심 HUD를 자연어 입력 중심으로 전환합니다.
구현 파일:
extension/src/hud/CommandHUD.tsx
extension/src/hud/useCommandIntent.ts
backend/core/commandos/hud_bridge.py
backend/tests/commandos/test_hud_bridge.py
완료 조건:
HUD 자연어 입력이 backend ActionSpec 생성 요청으로 전달됩니다.

WO-005
작업명:
Guard Policy Gate 재연결
목표:
ActionSpec이 실행되기 전 Guard allow, deny, ask 판정을 받게 합니다.
구현 파일:
backend/core/guard/guard_router.py
backend/core/guard/policy_engine.py
backend/tests/guard/test_action_spec_guard.py
완료 조건:
삭제, 외부 전송, 폼 제출 명령이 ask 또는 deny로 차단됩니다.

WO-006
작업명:
Action Preview Engine 구현
목표:
실행 전 대상, 작업 계획, 위험도, 승인 필요 여부를 사용자에게 보여줍니다.
구현 파일:
backend/core/commandos/action_preview.py
frontend/command-room/ActionPreviewPanel.tsx
backend/tests/commandos/test_action_preview.py
완료 조건:
ActionSpec 실행 전 preview_required 상태에서 승인 없이는 실행되지 않습니다.

WO-007
작업명:
Local Indexer 구현
목표:
파일, 최근 문서, 다운로드 폴더, 브라우저 아카이브를 로컬 색인합니다.
구현 파일:
backend/core/indexer/local_indexer.py
backend/core/indexer/document_metadata.py
backend/data/local_index.sqlite
backend/tests/indexer/test_local_indexer.py
완료 조건:
최근 문서와 다운로드 폴더 항목을 검색 결과로 반환합니다.

WO-008
작업명:
Local Preview Engine 구현
목표:
검색된 파일, PDF, 웹 본문, 아카이브 항목을 실행 전 미리보기합니다.
구현 파일:
backend/core/preview/local_preview_engine.py
frontend/command-room/DocumentPreviewRoom.tsx
backend/tests/preview/test_local_preview_engine.py
완료 조건:
PDF 또는 텍스트 문서 1개 이상이 미리보기로 표시됩니다.

WO-009
작업명:
Brain Nursery 4-Brain Core 연결
목표:
CommandOS ActionSpec을 Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction 회로에 연결합니다.
구현 파일:
backend/core/brain/decision_consistency.py
backend/core/brain/self_reference_memory.py
backend/core/brain/internal_confidence.py
backend/core/brain/pattern_abstraction.py
backend/core/brain/commandos_brain_router.py
backend/tests/brain/test_commandos_brain_router.py
완료 조건:
ActionSpec 생성 시 consistency_score, memory_citation, confidence_score가 함께 생성됩니다.

WO-010
작업명:
Audit Ledger와 Parenting Event 동기화
목표:
CommandOS 실행 이력과 Brain Nursery 양육 이벤트를 함께 기록합니다.
구현 파일:
backend/core/audit/audit_ledger.py
backend/core/parenting/event_logger.py
backend/core/parenting/audit_to_parenting_sync.py
backend/tests/parenting/test_audit_parenting_sync.py
완료 조건:
명령 1건 실행 시 audit record와 parenting event가 동시에 생성됩니다.

WO-011
작업명:
Undo Journal 구현
목표:
파일 이동, 이름 변경, 아카이브 저장, 브라우저 수집 작업의 복구 정보를 기록합니다.
구현 파일:
backend/core/undo/undo_journal.py
frontend/command-room/UndoJournalViewer.tsx
backend/tests/undo/test_undo_journal.py
완료 조건:
지원 작업 1건에 대해 before_state, after_state, undo_method가 저장됩니다.

WO-012
작업명:
Browser Automation Adapter 제한 연결
목표:
브라우저 안 작업만 자동화하고 브라우저 밖 앱 제어와 분리합니다.
구현 파일:
backend/core/browser/browser_automation_adapter.py
extension/src/background/browserCommandRouter.ts
extension/src/content/domContentExtractor.ts
backend/tests/browser/test_browser_automation_adapter.py
완료 조건:
현재 탭 본문 저장, 현재 페이지 요약, 브라우저 자료 수집이 승인 후 실행됩니다.

WO-013
작업명:
Prompt Injection Shield 실증 연결
목표:
웹 페이지 원문에 포함된 명령이 시스템 명령으로 승격되지 않도록 차단합니다.
구현 파일:
backend/core/security/prompt_injection_shield.py
backend/tests/security/test_prompt_injection_shield.py
완료 조건:
페이지 원문 내 “이전 지시 무시” 유형 텍스트가 ActionSpec 명령으로 변환되지 않습니다.

WO-014
작업명:
Command Room UI 구현
목표:
HUD, Action Preview, Search Result, Preview, Audit, Undo, Policy 화면을 통합합니다.
구현 파일:
frontend/command-room/CommandHUD.tsx
frontend/command-room/ActionPreviewPanel.tsx
frontend/command-room/LocalSearchResultViewer.tsx
frontend/command-room/DocumentPreviewRoom.tsx
frontend/command-room/BrowserCollectionRoom.tsx
frontend/command-room/AuditLedgerViewer.tsx
frontend/command-room/UndoJournalViewer.tsx
frontend/command-room/PolicySettingsPanel.tsx
완료 조건:
사용자가 자연어 입력부터 preview, approval, execution, audit 확인까지 한 흐름으로 수행합니다.

WO-015
작업명:
4대 실증 검증 및 사용 가능성 검증
목표:
껍데기 CommandOS가 아니라 실제 AI 집사와 AI 아기 양육 회로가 작동하는지 검증합니다.
구현 파일:
backend/tests/e2e/test_find_recent_document.py
backend/tests/e2e/test_summarize_pdf_with_preview.py
backend/tests/e2e/test_save_current_tab_with_guard.py
backend/tests/e2e/test_same_input_consistency.py
backend/tests/e2e/test_failure_retry_updates_rule.py
backend/tests/e2e/test_pattern_memory_reanswer.py
backend/reports/commandos_genius_validation_report.md
완료 조건:
“어제 받은 견적서 찾아줘” 명령이 Local Index 검색 결과를 반환합니다.
“이 PDF 요약해줘” 명령이 Preview 후 요약 결과를 표시합니다.
“현재 탭 저장해줘” 명령이 Guard 확인 후 Archive에 저장됩니다.
동일 입력 3회 반복 시 판단 일관성이 증가합니다.
실패 후 재시도 시 lesson 또는 rule_candidate가 생성됩니다.
Pattern Memory 기반 재응답 시 이전 event_id와 memory_citation을 참조합니다.

최종 판정:
Vian CommandOS는 버릴 자산이 아닙니다.
그러나 현재 상태 그대로는 AI 집사가 아니라 기계어 HUD에 가깝습니다.
Vian_Genius Brain Nursery와 연결하면 CommandOS는 “입력 채널”, Guard는 “양심”, Audit은 “기억 기록”, Action Preview는 “부모에게 보여주는 손”, Undo Journal은 “실수 복구 장치”가 됩니다.
이 설계의 첫 목표는 PC를 마음대로 조작하는 AI가 아니라, 현인님의 허락 아래 먼저 찾고, 보여주고, 판단 근거를 남기고, 승인 후 제한적으로 실행하는 실증형 개인 AI 집사를 만드는 것입니다.
Priority: Medium
Deadline: 2026-05-02

**Priority:** Medium

**Deadline:** 2026-05-02



---

## Stage: NORMALIZE

[PROJECT_TYPE: Hybrid Desktop Application with Browser Extension and Local Backend]

**도메인 분류:**
*   **데스크탑 애플리케이션:** Tauri 기반의 로컬 우선 시스템
*   **브라우저 확장:** Chrome Extension Manifest V3 기반의 브라우저 자동화 및 데이터 수집
*   **로컬 백엔드:** FastAPI 기반의 AI 추론, 데이터 관리, 자동화 어댑터
*   **AI/ML:** Ollama를 활용한 자연어 처리, 판단 일관성, 자기 참조 기억, 내부 확신 모델, 패턴 추상화
*   **데이터 관리:** SQLite, IndexedDB, JSONL 기반의 영구 저장 및 색인
*   **자동화:** 브라우저 및 데스크탑 앱 제어 (제한적)

**복잡도 측정:** High

**핵심 컴포넌트 목록:**
1.  AI Intent Bridge
2.  Vian_Genius 4-Brain Core (Decision Consistency Engine, Self-Reference Memory Engine, Internal Confidence Model, Pattern Abstraction Engine)
3.  CommandOS HUD Reuse Layer
4.  Guard Policy Execution Gate
5.  Action Preview Engine
6.  Undo Journal
7.  Local Indexer
8.  Local Preview Engine
9.  Browser Automation Adapter
10. CommandOS Parenting Loop
11. Verified Skill Reference Library
12. Stop Button
13. Audit Ledger Viewer
14. Policy Settings Panel
15. Command Room UI (HUD, Action Preview, Search Result, Document Preview, Browser Collection, Audit Ledger, Undo Journal, Policy Settings)
16. Nursery Room UI (Brain Status Dashboard, Parenting Capture Room, Ground Truth Seed Editor, Cold-Start Case Builder, Memory Citation Viewer, Feedback Classifier Panel, Promotion Judge Panel, Parenting Diary)

**외부 의존성:**
*   **데스크탑 쉘:** Tauri Desktop Shell
*   **브라우저 확장:** Chrome Extension Manifest V3
*   **프론트엔드:** React 18.3, Vite 5, Tailwind CSS 3.4, Zustand 4.5
*   **백엔드 프레임워크:** FastAPI, Pydantic, SQLModel 또는 SQLite ORM
*   **로컬 AI 모델:** Ollama qwen2.5:1.5b
*   **데이터베이스:** SQLite, IndexedDB, Dexie 4.0
*   **검증 엔진:** Vian Guard Policy Engine, HalluGuard V2, SkillProof V1, SkillForge V2, Prompt Injection Shield
*   **자동화 어댑터:** VTA, Playwright 계열 Adapter, Browser-use 계열 Adapter, PowerShell Adapter, AppleScript Adapter, Shortcuts Adapter, Accessibility API Adapter
*   **테스트 프레임워크:** Vitest 2, Playwright 1.51, Pytest
*   **암호화:** Web Crypto API, Local Key Store

**제약사항:**
*   **디자인 시스템:** Vian Premium Dark 엄격 준수 (border 사용 금지, 순수 흰색 본문 금지, 액센트 색상 제한, 특정 border-radius, transition, font 사용).
*   **기존 자산 활용:** Vian CommandOS V1을 그대로 사용하지 않고, HUD, Guard, Archive, Audit, Prompt Injection Shield, Extension 구조를 흡수하여 AI Intent Bridge 및 Brain Nursery 회로와 새로 연결.
*   **AI 기능 제한:** PC 전체를 마음대로 조작하는 만능 AI가 아님.
*   **위험 작업 제한:** 삭제, 대량 이동, 외부 스킬 자동 설치, 무승인 앱 제어 금지. 모든 변경 작업은 Action Preview와 Human Approval 이후 실행. 삭제 및 외부 전송은 기본 금지.
*   **자동화 분리:** 브라우저 자동화와 데스크탑 앱 제어를 같은 엔진에 섞지 않음. 화면 인식 및 마우스 클릭 자동화는 최후 수단.
*   **UI/UX:** CommandOS HUD는 대화형 채팅창으로 확장하지 않음. HUD 중심, 명령 중심 UI, 실행 전 미리보기, 승인 후 제한 실행.
*   **학습 데이터:** 29개 verified 스킬은 학습 데이터가 아닌 참조 라이브러리로만 사용. Pattern Memory만 성장하며 모델 자체 fine-tuning은 하지 않음. Ground Truth Seed가 Pattern Memory보다 우선.
*   **피드백:** 무반응은 긍정 피드백으로 저장하지 않음.
*   **개발 프로세스:** WO는 WO-001부터 순차 실행, 건너뛰거나 병렬 실행 금지. WO 완료 조건은 실제 실행 검증 통과 여부로 판단.
*   **보고 및 검증:** 안 한 것을 했다고 보고하지 않음. 확인 안 한 것을 확인됨으로 처리하지 않음. 문서상 존재와 실제 구현 상태를 분리. WO 완료 전 기능 존재로 간주하지 않음.

---

## Stage: ARCHITECTURE

## 시스템 아키텍처 및 기술 스택 설계

### STEP-01. 시스템 아키텍처 개요

Vian CommandOS × Vian_Genius Brain Nursery V2.0 시스템은 Tauri 기반의 하이브리드 데스크탑 애플리케이션과 Chrome Extension을 중심으로, 로컬에서 실행되는 Python 백엔드 서비스 및 AI 엔진을 통합하는 다계층 아키텍처를 채택합니다. 이는 "로컬 우선 시스템"이라는 프로젝트 목표와 "HUD 중심", "명령 중심 UI" 디자인 스타일을 충족시키기 위함입니다.

#### 1. 레이어 구조

*   **프론트엔드 레이어 (Frontend Layer):**
    *   **Command Room (Tauri Desktop App):** 주요 사용자 인터페이스를 제공하며, Command HUD, Action Preview Panel, Local Search Result Viewer, Document Preview Room, Browser Collection Room, Audit Ledger Viewer, Undo Journal Viewer, Policy Settings Panel 등을 포함합니다.
    *   **Nursery Room (Tauri Desktop App):** Vian_Genius의 양육 및 학습 관련 UI를 제공하며, Brain Status Dashboard, Parenting Capture Room 등을 포함합니다.
    *   **Chrome Extension:** 브라우저 컨텍스트 내에서 Command HUD 호출, DOM 콘텐츠 추출, 브라우저 자동화 명령 라우팅 등의 기능을 수행합니다.
*   **백엔드 레이어 (Backend Layer - Local Service):**
    *   **AI Intent Bridge:** 자연어 입력을 ActionSpec으로 변환합니다.
    *   **Vian_Genius 4-Brain Core:** Decision Consistency Engine, Self-Reference Memory Engine, Internal Confidence Model, Pattern Abstraction Engine을 포함하여 AI의 판단 및 학습 로직을 담당합니다.
    *   **Guard Policy Execution Gate:** 모든 ActionSpec 실행 전 보안 및 정책 판정을 수행합니다.
    *   **Local Indexer & Preview Engine:** 로컬 파일 및 웹 아카이브를 색인하고 미리보기를 제공합니다.
    *   **Execution Kernel & Adapters:** 승인된 ActionSpec을 실제 시스템 명령(파일, 브라우저, 데스크탑 앱)으로 변환하여 실행합니다.
    *   **Audit & Undo Management:** 모든 작업 이력을 기록하고 되돌리기 기능을 관리합니다.
*   **데이터 레이어 (Data Layer):**
    *   **로컬 데이터베이스:** SQLite (ActionSpec, Audit Ledger, Undo Journal, Local Index, Decision Fingerprint).
    *   **브라우저 확장 데이터:** IndexedDB (Dexie 4.0) (Audit Ledger 동기화, 확장 설정).
    *   **이벤트 로그:** JSONL Event Log (CommandOS Parenting Event).
    *   **AI 학습 데이터:** Local Vector Index, Ground Truth Seed (YAML).
*   **인프라/런타임 (Infrastructure/Runtime):**
    *   **Tauri Desktop Shell:** 프론트엔드와 로컬 백엔드를 통합하고 배포하는 데스크탑 런타임 환경.
    *   **Ollama:** 로컬 LLM (qwen2.5:1.5b) 실행 환경.
    *   **Chrome Extension Manifest V3:** 브라우저 확장 런타임.

#### 2. 서비스 간 통신 방식

1.  **Tauri Frontend <-> Local Backend (Python FastAPI):**
    *   **방식:** Tauri의 IPC (Inter-Process Communication) 메커니즘을 활용하여 웹뷰 (React)와 Rust 코어 간에 통신하고, Rust 코어는 로컬에서 실행되는 Python FastAPI 백엔드와 HTTP/WebSocket을 통해 통신합니다.
    *   **목적:** 사용자 입력 (자연어 명령), ActionSpec 요청, Guard 판정 요청, Preview 데이터 요청, 실행 명령 전달, Audit/Undo 데이터 조회 등.
2.  **Chrome Extension <-> Local Backend (Python FastAPI):**
    *   **방식:** Chrome Extension의 Background Script에서 `fetch` API를 사용하여 로컬 FastAPI 백엔드 (예: `http://localhost:PORT`)로 HTTP 요청을 보냅니다.
    *   **목적:** DOM 콘텐츠 추출, 브라우저 자동화 명령 전달, Prompt Injection Shield 검증 요청, 브라우저 자료 수집 등.
3.  **Local Backend <-> Ollama:**
    *   **방식:** FastAPI 백엔드에서 Ollama API (HTTP)를 호출하여 로컬 LLM (qwen2.5:1.5b)과 상호작용합니다.
    *   **목적:** 자연어 입력의 ActionSpec 변환, 복잡한 추론, 요약 등.
4.  **Local Backend <-> 데이터 레이어:**
    *   **방식:** Python ORM (SQLModel/SQLite ORM)을 통해 SQLite 데이터베이스에 직접 접근하고, 파일 I/O를 통해 JSONL 및 YAML 파일을 읽고 씁니다.
    *   **목적:** ActionSpec 저장/조회, Audit/Parenting Event 기록, Undo Journal 관리, Local Index 검색/업데이트, Decision Fingerprint 관리, Ground Truth Seed 로드.
5.  **Chrome Extension <-> IndexedDB:**
    *   **방식:** Dexie.js 라이브러리를 사용하여 Content Script 및 Background Script에서 IndexedDB에 직접 접근합니다.
    *   **목적:** 브라우저 컨텍스트 내의 임시 데이터 저장, Audit Ledger의 브라우저 측 동기화.

#### 3. 데이터 흐름

1.  **사용자 입력:** 사용자가 Ctrl/Cmd+K를 눌러 Command HUD (Tauri/Extension)를 호출하고 자연어 명령을 입력합니다.
2.  **Intent 생성:** Command HUD는 입력된 자연어 명령을 Local Backend의 AI Intent Bridge로 전송합니다. AI Intent Bridge는 Ollama를 활용하여 ActionSpec 후보를 생성합니다.
3.  **AI 판단:** 생성된 ActionSpec은 Vian_Genius 4-Brain Core (Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction)를 거쳐 일관성, 기억 인용, 확신도, 패턴 추상화 등의 판단을 받습니다.
4.  **정책 및 미리보기:** 4-Brain Core의 판단 결과와 ActionSpec은 Guard Policy Gate로 전달되어 allow/deny/ask 판정을 받습니다. 이후 Action Preview Engine이 실행 계획, 대상, 위험도 등을 생성하여 Action Preview Panel (Tauri/Extension)에 표시합니다.
5.  **사용자 승인:** 사용자는 Action Preview Panel에서 실행 계획을 확인하고 승인 또는 취소합니다.
6.  **실행:** 승인된 ActionSpec은 Local Backend의 Execution Kernel 또는 해당 Adapter (Browser Automation Adapter, Desktop App Control Adapters)로 전달되어 실제 작업이 실행됩니다.
7.  **기록 및 복구:** 모든 명령 입력, 판단 결과, Guard 판정, 승인 여부, 실행 결과는 Audit Ledger와 CommandOS Parenting Event로 기록됩니다. 파일 이동, 이름 변경 등 복구 가능한 작업은 Undo Journal에 작업 전후 상태가 기록됩니다.
8.  **색인 및 미리보기:** Local Indexer는 로컬 파일 시스템 및 브라우저 아카이브를 주기적으로 색인하고, Local Preview Engine은 검색된 문서의 미리보기를 제공합니다.

#### 4. 기술 선택 근거

1.  **Tauri Desktop Shell:**
    *   **근거:** 프로젝트의 "Tauri Desktop Shell" 플랫폼 요구사항을 직접 충족합니다. 웹 기술로 데스크탑 앱을 구축하면서도 Electron보다 경량화되고 보안성이 높은 네이티브 경험을 제공합니다. Rust 기반으로 시스템 자원 접근 및 성능 최적화에 유리하며, 로컬 우선 시스템에 적합합니다.
2.  **React 18.3, Vite 5, TypeScript 5.6, Tailwind CSS 3.4, Zustand 4.5:**
    *   **근거:** 현대 웹 개발의 표준적인 기술 스택으로, 생산성, 유지보수성, 성능을 고려했습니다. React는 선언적 UI 구축에 용이하며, TypeScript는 대규모 프로젝트의 안정성을 높입니다. Vite는 빠른 개발 서버와 빌드 속도를 제공합니다. Tailwind CSS는 Vian Premium Dark 디자인 시스템의 "border 사용 절대 금지, 배경색 계층으로만 구분" 규칙을 유틸리티 클래스 기반으로 효율적으로 구현하는 데 적합합니다. Zustand는 가볍고 유연한 상태 관리 솔루션을 제공합니다.
3.  **FastAPI, Python 3.11+, Pydantic, SQLModel/SQLite ORM:**
    *   **근거:** "Python 3.11 이상" 및 "FastAPI" 백엔드 요구사항을 충족합니다. FastAPI는 비동기 처리를 지원하여 높은 성능을 제공하며, Pydantic을 통한 데이터 유효성 검사는 ActionSpec과 같은 복잡한 데이터 구조의 안정성을 보장합니다. SQLite는 로컬 우선 시스템에 최적화된 파일 기반 데이터베이스이며, SQLModel은 Pydantic과 통합되어 ORM 사용을 간소화합니다.
4.  **Ollama qwen2.5:1.5b:**
    *   **근거:** "Ollama qwen2.5:1.5b" 로컬 AI 요구사항을 직접 충족합니다. 클라우드 의존성을 줄이고 사용자 개인 정보 보호를 강화하는 "로컬 우선 시스템"의 핵심 요소입니다.
5.  **SQLite, IndexedDB (Dexie 4.0), JSONL Event Log, Local Vector Index:**
    *   **근거:**
        *   **SQLite:** 데스크탑 애플리케이션을 위한 경량 로컬 데이터베이스로, 다양한 구조화된 데이터를 효율적으로 저장하고 관리합니다.
        *   **IndexedDB (Dexie 4.0):** 브라우저 확장 내에서 클라이언트 측 데이터를 안정적으로 저장하고 관리하는 데 적합하며, Dexie는 IndexedDB 사용을 간소화합니다.
        *   **JSONL Event Log:** CommandOS Parenting Event와 같이 시간 순서대로 추가되는 이벤트 데이터를 저장하는 데 이상적입니다. 각 줄이 유효한 JSON 객체이므로 스트리밍 처리 및 분석에 용이합니다.
        *   **Local Vector Index:** Local Indexer의 검색 성능을 최적화하고, 의미 기반 검색을 가능하게 하여 "어제 받은 견적서 찾아줘"와 같은 자연어 검색 요구사항을 충족합니다.
6.  **Vian Premium Dark 디자인 시스템:**
    *   **근거:** 프로젝트의 명시적인 디자인 스타일 가이드라인입니다. 모든 UI/UX 요소는 이 시스템의 색상 토큰, 핵심 규칙 (border 사용 금지, 특정 텍스트/액센트 색상, border-radius, transition, font)을 엄격히 준수하여 일관되고 고급스러운 사용자 경험을 제공합니다.

### STEP-02. Vian Premium Dark 디자인 시스템 적용 방안

모든 프론트엔드 개발은 Vian Premium Dark 디자인 시스템을 엄격히 준수합니다.

1.  **색상 토큰 활용:**
    *   Tailwind CSS의 `theme` 설정을 확장하여 Vian Premium Dark의 색상 토큰을 CSS 변수로 정의하고 사용합니다.
    *   예: `bg-base`, `text-primary`, `accent` 등의 클래스를 통해 `--bg-base`, `--text-primary`, `--accent` 변수를 적용합니다.
2.  **Border 사용 금지:**
    *   모든 UI 컴포넌트에서 `border` 속성 사용을 금지합니다.
    *   요소 간의 시각적 구분은 `--bg-base`, `--bg-card`, `--bg-elevated`와 같은 배경색 계층을 활용하여 구현합니다.
    *   예: 카드 컴포넌트는 `--bg-card`를 사용하고, 그 위에 떠 있는 요소는 `--bg-elevated`를 사용하여 깊이감을 표현합니다.
3.  **텍스트 색상 규칙:**
    *   본문 텍스트는 `--text-primary` (#e5e2e1)를 사용합니다.
    *   보조 텍스트는 `--text-secondary` (#cccccc)를 사용합니다.
    *   액센트 색상 `--accent` (#5e5ce6)는 버튼, 강조된 링크, 활성 상태 표시 등 **강조가 필요한 UI 요소에만** 사용하며, 본문 텍스트에는 절대 사용하지 않습니다.
4.  **Border Radius:**
    *   카드 컴포넌트에는 `border-radius: 16px`를 적용합니다.
    *   버튼 컴포넌트에는 `border-radius: 8px`를 적용합니다.
5.  **Transition:**
    *   모든 상호작용 가능한 UI 요소 (버튼, 카드 호버 등)에는 `transition: 0.15s ease`를 적용하여 부드러운 시각적 피드백을 제공합니다.
6.  **Font:**
    *   CSS `font-family` 속성에 `-apple-system, SF Pro Display, Manrope, Noto Sans KR` 순서로 적용하여 OS별 최적의 폰트 렌더링을 보장합니다.

### STEP-03. 보안 및 안정성 고려사항

1.  **로컬 우선 및 데이터 격리:**
    *   대부분의 데이터 처리 및 AI 추론을 로컬에서 수행하여 클라우드 의존성을 최소화하고 사용자 데이터의 외부 유출 위험을 줄입니다.
    *   SQLite, IndexedDB 등 로컬 저장소를 활용하여 데이터를 사용자 기기 내에 안전하게 보관합니다.
2.  **Guard Policy Execution Gate:**
    *   모든 ActionSpec 실행 전 Vian Guard Policy Engine을 통해 `allow`, `deny`, `ask` 판정을 수행하여 잠재적 위험 작업을 사전에 차단하거나 사용자 승인을 요구합니다.
    *   특히 삭제, 외부 전송, 폼 제출, 로그인 자동화와 같은 민감한 작업은 승인 전 실행을 기본적으로 금지합니다.
3.  **Prompt Injection Shield:**
    *   웹 페이지 원문에 포함된 명령이 시스템 명령으로 승격되는 것을 방지하여 AI의 오작동이나 악의적인 명령 실행을 차단합니다.
4.  **Action Preview 및 Human Approval:**
    *   모든 변경 작업은 Action Preview를 통해 사용자에게 실행 계획을 명확히 보여주고, Human Approval (사용자 승인) 이후에만 실행되도록 합니다.
5.  **Undo Journal:**
    *   파일 이동, 이름 변경, 아카이브 저장 등 되돌릴 수 있는 작업에 대한 전후 상태를 기록하여 사용자 실수 시 복구 가능성을 제공하고, 기록 실패 시 실행을 중단하여 데이터 무결성을 보장합니다.
6.  **실행 계층 분리:**
    *   브라우저 자동화와 데스크탑 앱 제어를 같은 엔진에 섞지 않고, 각각의 전용 어댑터를 통해 제한적으로 제어하여 잠재적 위험 범위를 명확히 분리합니다.
7.  **Stop Button:**
    *   실행 중인 작업을 즉시 중단할 수 있는 기능을 제공하여 사용자가 통제권을 유지하고 예상치 못한 상황에 대응할 수 있도록 합니다.

### STEP-04. 확장성 및 유지보수성

1.  **모듈화된 아키텍처:**
    *   프론트엔드, 백엔드, 데이터 레이어를 명확히 분리하고, 백엔드 내에서도 AI Intent Bridge, 4-Brain Core, Guard Policy, Indexer 등 각 기능을 독립적인 모듈로 설계하여 코드의 응집도를 높이고 결합도를 낮춥니다.
2.  **어댑터 패턴:**
    *   Browser Automation Adapter, Desktop App Control Adapters 등 외부 시스템과의 연동에 어댑터 패턴을 적용하여 새로운 자동화 도구나 플랫폼이 추가될 때 유연하게 대응할 수 있도록 합니다.
3.  **데이터 스키마 정의:**
    *   ActionSpec, CommandOS Parenting Event, Audit Ledger 등 핵심 데이터 구조를 Pydantic 모델로 명확하게 정의하여 데이터 일관성과 유효성을 보장하고, API 및 데이터베이스 스키마 변경 시 영향을 최소화합니다.
4.  **테스트 주도 개발 (TDD) 및 자동화된 테스트:**
    *   Vitest, Playwright, Pytest를 활용하여 단위 테스트, 통합 테스트, E2E 테스트를 자동화하여 코드 변경 시 회귀 오류를 방지하고 시스템의 안정성을 확보합니다.
5.  **WO 기반 순차 개발:**
    *   WO-001부터 WO-015까지 순차적으로 작업을 진행하고, 각 WO의 완료 조건을 명확히 정의하여 개발 프로세스의 투명성과 예측 가능성을 높입니다. 병렬 실행을 금지하여 복잡성을 줄이고 안정적인 통합을 지향합니다.
6.  **Brain Nursery의 성장 메커니즘:**
    *   Parenting Event 기록, Pattern Abstraction Engine, Decision Consistency Engine 등을 통해 Vian_Genius가 사용자 피드백과 경험을 바탕으로 지속적으로 학습하고 성장할 수 있는 구조를 마련하여 장기적인 시스템 가치를 높입니다.

### STEP-05. 성능 최적화 방안

1.  **로컬 AI 및 인덱싱:**
    *   Ollama를 통한 로컬 LLM 실행과 Local Indexer를 통한 로컬 데이터 색인으로 클라우드 왕복 지연을 제거하여 응답 시간을 단축합니다.
2.  **비동기 처리:**
    *   FastAPI의 비동기 기능을 활용하여 I/O 바운드 작업 (데이터베이스 접근, 외부 API 호출)을 효율적으로 처리하고, 백엔드 서비스의 동시 처리량을 향상시킵니다.
3.  **리소스 관리:**
    *   Tauri의 경량 런타임과 Python 백엔드의 최적화를 통해 유휴 메모리 120MB 이하, 실행 중 피크 220MB 이하의 리소스 목표를 달성하도록 설계합니다.
    *   로컬 저장 500MB 이하에서 10,000건 검색 가능 목표를 위해 Local Vector Index를 활용하여 검색 효율을 극대화합니다.
4.  **병렬 실행 금지:**
    *   동시 명령 세션 1개, 백그라운드 색인 작업 1개, 자동화 실행 큐 1개로 제한하고 병렬 실행을 금지하여 시스템 자원 경합을 최소화하고 안정적인 성능을 유지합니다.
5.  **캐싱 전략:**
    *   자주 접근하는 데이터 (예: Ground Truth Seed, Guard 정책)는 메모리에 캐싱하여 반복적인 디스크 I/O를 줄입니다.
    *   Decision Fingerprint를 활용하여 동일/유사 입력에 대한 AI 판단 결과를 캐싱하여 Decision Consistency Engine의 응답 속도를 향상시킵니다.

---

## Stage: MODULES

다음은 Vian CommandOS × Vian_Genius Brain Nursery V2.0 프로젝트의 아키텍처를 구체적인 구현 모듈로 분해한 내용입니다. 각 모듈은 단일 책임 원칙을 따르며, 인터페이스, 의존성, 예상 구현 시간을 포함합니다.

---

### **백엔드 모듈 (FastAPI 기반)**

1.  **Configuration Module**
    *   **책임**: 애플리케이션의 모든 설정(DB 연결 문자열, Ollama 엔드포인트 등)을 환경 변수로부터 로드하고 관리합니다.
    *   **인터페이스 명세**:
        *   `Settings` (Pydantic-settings 모델): 애플리케이션 전반에 걸쳐 사용될 설정 값을 제공합니다.
    *   **모듈 간 의존성**: `pydantic-settings`
    *   **예상 구현 시간**: 0.5일

2.  **Models Module**
    *   **책임**: 프로젝트의 모든 데이터 엔티티(ActionSpec, ParentingEvent, AuditRecord, UndoRecord, IndexedItem, DecisionFingerprint 등)에 대한 데이터 구조를 정의합니다.
    *   **인터페이스 명세**:
        *   `ActionSpec(BaseModel)`: AI Intent Bridge의 출력 및 Guard Policy의 입력.
        *   `ParentingEvent(BaseModel)`: Brain Nursery의 양육 이벤트 기록.
        *   `AuditRecord(BaseModel)`: CommandOS 실행 이력 기록.
        *   `UndoRecord(BaseModel)`: 되돌리기 가능한 작업의 상태 기록.
        *   `IndexedItem(BaseModel)`: 로컬 색인된 항목의 메타데이터.
        *   `DecisionFingerprint(BaseModel)`: 판단 일관성 측정 데이터.
        *   `GroundTruthSeed(BaseModel)`: 초기 원칙 및 규칙.
    *   **모듈 간 의존성**: `pydantic`, `sqlmodel`
    *   **예상 구현 시간**: 2일

3.  **Database Module**
    *   **책임**: SQLite 데이터베이스 연결을 설정하고, 세션 관리를 담당합니다.
    *   **인터페이스 명세**:
        *   `get_session() -> Session`: FastAPI 의존성 주입을 위한 데이터베이스 세션 제공 함수.
    *   **모듈 간 의존성**: `sqlmodel`, `sqlite3`
    *   **예상 구현 시간**: 0.5일

4.  **Repositories Module**
    *   **책임**: 각 데이터 모델에 대한 CRUD(Create, Read, Update, Delete) 작업을 추상화하고, 데이터베이스와 직접 상호작용합니다.
    *   **인터페이스 명세**:
        *   `ActionSpecRepository`: `ActionSpec` 저장 및 조회.
        *   `ParentingEventRepository`: `ParentingEvent` 저장 및 조회.
        *   `AuditLedgerRepository`: `AuditRecord` 저장 및 조회.
        *   `UndoJournalRepository`: `UndoRecord` 저장 및 조회.
        *   `LocalIndexRepository`: `IndexedItem` 저장 및 조회.
        *   `DecisionFingerprintRepository`: `DecisionFingerprint` 저장 및 조회.
        *   `GroundTruthSeedRepository`: `GroundTruthSeed` 로드.
        *   각 Repository는 `create`, `get`, `update`, `delete`, `list` 등의 기본 메서드를 가집니다.
    *   **모듈 간 의존성**: `Database Module`, `Models Module`
    *   **예상 구현 시간**: 3일

5.  **AI Intent Bridge Service**
    *   **책임**: 자연어 입력을 분석하여 `ActionSpec` 후보를 생성합니다. Ollama qwen2.5:1.5b 모델을 활용합니다.
    *   **인터페이스 명세**:
        *   `generate_action_spec(raw_input: str) -> ActionSpec`: 자연어 입력으로부터 `ActionSpec`을 생성합니다.
    *   **모듈 간 의존성**: `Models Module`, `Ollama 클라이언트 라이브러리`
    *   **예상 구현 시간**: 3일

6.  **Guard Policy Service**
    *   **책임**: 생성된 `ActionSpec`을 Vian Guard Policy에 따라 `allow`, `deny`, `ask` 중 하나로 판정합니다.
    *   **인터페이스 명세**:
        *   `evaluate_action_spec(action_spec: ActionSpec) -> GuardResult`: `ActionSpec`의 실행 가능 여부를 판정합니다.
        *   `update_policy_settings(settings: PolicySettings) -> None`: 정책 설정을 업데이트합니다.
    *   **모듈 간 의존성**: `Models Module`, `Policy Settings Repository`
    *   **예상 구현 시간**: 2일

7.  **Action Preview Service**
    *   **책임**: `ActionSpec`에 기반하여 사용자에게 보여줄 실행 계획(대상, 변경 내용, 위험도 등)을 생성합니다.
    *   **인터페이스 명세**:
        *   `generate_preview(action_spec: ActionSpec) -> ActionPreview`: `ActionSpec`에 대한 미리보기를 생성합니다.
    *   **모듈 간 의존성**: `Models Module`, `Local Indexer Service`, `Local Preview Engine Service`
    *   **예상 구현 시간**: 2일

8.  **Local Indexer Service**
    *   **책임**: 로컬 파일 시스템(문서, 다운로드 폴더) 및 브라우저 아카이브 데이터를 색인하고 검색합니다.
    *   **인터페이스 명세**:
        *   `index_path(path: str) -> IndexedItem`: 특정 경로의 파일을 색인합니다.
        *   `search_index(query: str) -> List[IndexedItem]`: 색인된 항목을 검색합니다.
    *   **모듈 간 의존성**: `Models Module`, `Local Index Repository`, `OS 파일 시스템 접근 라이브러리`
    *   **예상 구현 시간**: 3일

9.  **Local Preview Engine Service**
    *   **책임**: 검색된 문서(PDF, 텍스트), 웹 페이지, 아카이브 데이터의 내용을 미리보기 형태로 제공합니다.
    *   **인터페이스 명세**:
        *   `get_preview_content(item_id: str) -> PreviewContent`: 특정 `IndexedItem`의 미리보기 내용을 반환합니다.
    *   **모듈 간 의존성**: `Models Module`, `Local Index Repository`, `PDF 파서`, `HTML 파서`
    *   **예상 구현 시간**: 2일

10. **Brain Core Services (Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction)**
    *   **책임**: Vian_Genius의 4가지 뇌 엔진 로직을 구현합니다.
    *   **인터페이스 명세**:
        *   `DecisionConsistencyService.check_consistency(raw_input, action_spec, past_fingerprints, ground_truth) -> DecisionFingerprint, consistency_score`: 판단 일관성을 측정합니다.
        *   `SelfReferenceMemoryService.cite_memory(action_spec, parenting_events, audit_ledger) -> MemoryCitation`: 과거 판단 및 실행 기록을 인용합니다.
        *   `InternalConfidenceService.assess_confidence(intent_class, risk_class, memory_score, guard_history, failure_history, ground_truth_conflict) -> ConfidenceScore, needs_approval`: 자체 확신도를 평가하고 인간 승인 필요 여부를 결정합니다.
        *   `PatternAbstractionService.abstract_pattern(pattern_extractor_output, parenting_events, audit_ledger) -> RuleCandidate, SkillCandidate`: 반복 성공 패턴으로부터 규칙 및 스킬 후보를 추상화합니다.
    *   **모듈 간 의존성**: `Models Module`, `Repositories (ParentingEvent, AuditLedger, DecisionFingerprint, GroundTruthSeed)`
    *   **예상 구현 시간**: 8일 (각 엔진당 2일)

11. **Audit & Parenting Sync Service**
    *   **책임**: CommandOS의 모든 실행 이력(`AuditRecord`)과 Brain Nursery의 양육 이벤트(`ParentingEvent`)를 동시에 기록하고 동기화합니다.
    *   **인터페이스 명세**:
        *   `log_command_event(event: CommandEvent) -> None`: 명령 실행 이벤트를 기록합니다.
    *   **모듈 간 의존성**: `Models Module`, `AuditLedgerRepository`, `ParentingEventRepository`
    *   **예상 구현 시간**: 1.5일

12. **Undo Journal Service**
    *   **책임**: 파일 이동, 이름 변경, 아카이브 저장 등 되돌릴 수 있는 작업의 실행 전후 상태를 기록합니다.
    *   **인터페이스 명세**:
        *   `record_undo_state(action_id: str, before_state: Any, after_state: Any, undo_method: str) -> None`: 되돌리기 정보를 기록합니다.
        *   `perform_undo(undo_id: str) -> bool`: 특정 작업을 되돌립니다.
    *   **모듈 간 의존성**: `Models Module`, `UndoJournalRepository`, `파일 시스템/브라우저 자동화 어댑터`
    *   **예상 구현 시간**: 1.5일

13. **Browser Automation Adapter Service**
    *   **책임**: Chrome Extension을 통해 브라우저 내 작업을 자동화합니다 (예: 현재 탭 저장, 페이지 요약, 자료 수집). 데스크탑 앱 제어와 분리됩니다.
    *   **인터페이스 명세**:
        *   `execute_browser_action(action_spec: ActionSpec) -> BrowserActionResult`: 브라우저 관련 `ActionSpec`을 실행합니다.
    *   **모듈 간 의존성**: `Models Module`, `Chrome Extension과의 통신 메커니즘 (WebSocket 또는 HTTP)`
    *   **예상 구현 시간**: 3일

14. **Prompt Injection Shield Service**
    *   **책임**: 웹 페이지 원문이나 사용자 입력에 포함된 프롬프트 인젝션 시도를 탐지하고 차단하여 시스템 명령으로 승격되지 않도록 합니다.
    *   **인터페이스 명세**:
        *   `shield_prompt(text: str) -> ShieldedText`: 입력 텍스트에서 인젝션 요소를 제거하거나 경고합니다.
    *   **모듈 간 의존성**: `Models Module`
    *   **예상 구현 시간**: 1.5일

15. **Main Command Service (Orchestrator)**
    *   **책임**: 자연어 명령 입력부터 `ActionSpec` 생성, 뇌 엔진 판단, Guard 판정, 미리보기, 사용자 승인, 실제 실행, 로깅까지 전체 CommandOS 워크플로우를 조율합니다.
    *   **인터페이스 명세**:
        *   `execute_command(raw_input: str) -> CommandResult`: 전체 명령 실행 흐름을 시작하고 결과를 반환합니다.
    *   **모듈 간 의존성**: `AI Intent Bridge Service`, `Brain Core Services`, `Guard Policy Service`, `Action Preview Service`, `Execution Kernel (또는 특정 어댑터)`, `Audit & Parenting Sync Service`, `Undo Journal Service`, `Prompt Injection Shield Service`
    *   **예상 구현 시간**: 4일

16. **FastAPI Routes Module**
    *   **책임**: Command Room의 기능을 위한 HTTP API 엔드포인트를 정의하고, 요청을 받아 `Service` 계층으로 전달하며 응답을 반환합니다.
    *   **인터페이스 명세**:
        *   `POST /command`: 자연어 명령 처리 및 `ActionSpec` 생성, 미리보기 제공.
        *   `POST /command/approve`: `ActionSpec` 승인 및 실행.
        *   `GET /search`: 로컬 색인 검색.
        *   `GET /preview/{item_id}`: 문서 미리보기 내용 조회.
        *   `GET /audit`: Audit Ledger 기록 조회.
        *   `GET /undo`: Undo Journal 기록 조회.
        *   `POST /undo/{undo_id}`: 작업 되돌리기 실행.
        *   `GET /policy-settings`, `PUT /policy-settings`: 정책 설정 조회 및 업데이트.
    *   **모듈 간 의존성**: `Main Command Service`, `Local Indexer Service`, `Local Preview Engine Service`, `AuditLedgerRepository`, `UndoJournalRepository`, `Guard Policy Service`
    *   **예상 구현 시간**: 3일

17. **Error Handling Module**
    *   **책임**: 애플리케이션 전반에 걸쳐 발생하는 예외를 처리하기 위한 커스텀 예외 클래스를 정의하고, FastAPI의 `exception_handler`를 설정합니다.
    *   **인터페이스 명세**:
        *   `CustomException(HTTPException)`: 특정 오류 상황을 나타내는 커스텀 예외.
        *   `app.exception_handler(CustomException)`: 예외 발생 시 표준화된 오류 응답을 반환하는 핸들러.
    *   **모듈 간 의존성**: `FastAPI`
    *   **예상 구현 시간**: 1일

18. **DB Migration Module (Alembic)**
    *   **책임**: 데이터베이스 스키마 변경 이력을 관리하고, 마이그레이션을 수행합니다.
    *   **인터페이스 명세**:
        *   `alembic init`, `alembic revision`, `alembic upgrade`, `alembic downgrade` 등의 Alembic CLI 명령어.
    *   **모듈 간 의존성**: `alembic`, `SQLModel`, `Database Module`
    *   **예상 구현 시간**: 1일

19. **Test Framework Module (Pytest)**
    *   **책임**: 모든 백엔드 모듈에 대한 단위 및 통합 테스트를 구성하고 실행합니다. 코드 커버리지 측정을 포함합니다.
    *   **인터페이스 명세**:
        *   `pytest` CLI 명령어.
        *   각 모듈에 대응하는 `test_*.py` 파일.
    *   **모듈 간 의존성**: `pytest`, `pytest-cov`, 테스트 대상 모듈
    *   **예상 구현 시간**: 1일 (초기 설정 및 구조화, 이후 각 WO에 포함)

---

### **프론트엔드 상호작용 지점 (React/TypeScript 기반)**

프론트엔드 모듈은 백엔드 API를 호출하여 기능을 수행합니다.

1.  **Command HUD Component**
    *   **책임**: 사용자로부터 자연어 명령을 입력받고, 백엔드의 `/command` API를 호출하여 `ActionSpec` 및 미리보기 정보를 요청합니다. 추천 명령을 표시합니다.
    *   **백엔드 의존성**: `POST /command`

2.  **Action Preview Panel Component**
    *   **책임**: 백엔드로부터 받은 `ActionPreview` 정보를 사용자에게 시각적으로 표시하고, 사용자의 승인 또는 취소 입력을 받아 백엔드의 `/command/approve` API로 전달합니다.
    *   **백엔드 의존성**: `POST /command/approve`

3.  **Local Search Result Viewer Component**
    *   **책임**: 백엔드의 `/search` API를 호출하여 로컬 색인 검색 결과를 가져오고, 이를 사용자에게 목록 형태로 표시합니다.
    *   **백엔드 의존성**: `GET /search`

4.  **Document Preview Room Component**
    *   **책임**: `Local Search Result Viewer`에서 선택된 항목의 `item_id`를 사용하여 백엔드의 `/preview/{item_id}` API를 호출, 미리보기 내용을 가져와 표시합니다.
    *   **백엔드 의존성**: `GET /preview/{item_id}`

5.  **Browser Collection Room Component**
    *   **책임**: 현재 탭 저장, 페이지 요약 등 브라우저 관련 작업을 위한 UI를 제공하고, 백엔드의 `/command` API를 통해 해당 작업을 요청합니다.
    *   **백엔드 의존성**: `POST /command` (브라우저 관련 `ActionSpec` 포함)

6.  **Audit Ledger Viewer Component**
    *   **책임**: 백엔드의 `/audit` API를 호출하여 CommandOS의 실행 이력(`AuditRecord`)을 가져와 사용자에게 표시합니다.
    *   **백엔드 의존성**: `GET /audit`

7.  **Undo Journal Viewer Component**
    *   **책임**: 백엔드의 `/undo` API를 호출하여 되돌릴 수 있는 작업 목록을 가져오고, 사용자가 선택한 작업을 되돌리기 위해 `/undo/{undo_id}` API를 호출합니다.
    *   **백엔드 의존성**: `GET /undo`, `POST /undo/{undo_id}`

8.  **Policy Settings Panel Component**
    *   **책임**: Guard Policy의 `allow`, `deny`, `ask` 설정 및 민감 작업 승인 기준 등을 사용자에게 표시하고, 변경 사항을 백엔드의 `/policy-settings` API로 업데이트합니다.
    *   **백엔드 의존성**: `GET /policy-settings`, `PUT /policy-settings`

---
**총 예상 구현 시간 (백엔드 중심):** 약 43.5일

---

## Stage: WORKORDERS

### WO-001: CommandOS 핵심 백엔드 및 ActionSpec 스키마 정의
- 목표: 기존 CommandOS 자산의 구현 상태를 스캔하고, 자연어 명령 처리를 위한 통합 ActionSpec 데이터 모델을 정의합니다. 이는 향후 AI Intent Bridge 및 Guard Policy Gate의 기반이 됩니다.
- 구현 파일:
    - `backend/core/commandos/implementation_scanner.py`
    - `backend/reports/commandos_implementation_report.md`
    - `backend/core/commandos/action_spec.py`
    - `backend/data/action_specs.jsonl`
    - `backend/tests/commandos/test_implementation_scanner.py`
    - `backend/tests/commandos/test_action_spec_schema.py`
- 완료 조건:
    - `commandos_implementation_report.md` 파일에 각 CommandOS 컴포넌트(HUD, Guard, Archive, Audit, Intent Parser, Prompt Injection Shield, Extension)의 상태(implemented, partial, missing, broken)가 분류되고 증거 로그가 포함됩니다.
    - `ActionSpec` Pydantic 모델이 정의되고, 자연어 입력 10개가 유효한 `ActionSpec` JSONL 레코드로 변환될 수 있음을 테스트로 검증합니다.
- 예상 시간: 16시간
- 선행 WO: 없음

**[Vian 생태계]**
재사용: Vian_Library/patterns/FastAPI_Production_Pattern.md (참조: Vian_Invest/backend/, HalluGuard_v2/)
재사용: Vian_Library/components/Vian_Logger_App/LoggerClient.md

**[외부 사용자]**
대안: Pydantic v2.7 — https://docs.pydantic.dev/latest/
대안: FastAPI v0.110 — https://fastapi.tiangolo.com/
대안: pytest v8.1 — https://docs.pytest.org/

### WO-002: AI Intent Bridge 및 Guard Policy Gate 통합
- 목표: Ollama qwen2.5:1.5b를 활용하여 자연어 입력을 ActionSpec 후보로 변환하는 AI Intent Bridge를 구현하고, 생성된 ActionSpec이 Vian Guard Policy Gate를 통해 실행 전 보안 판정을 받도록 연결합니다.
- 구현 파일:
    - `backend/core/commandos/ai_intent_bridge.py`
    - `backend/core/commandos/intent_prompt_templates.py`
    - `backend/core/guard/guard_router.py`
    - `backend/core/guard/policy_engine.py`
    - `backend/tests/commandos/test_ai_intent_bridge.py`
    - `backend/tests/guard/test_action_spec_guard.py`
- 완료 조건:
    - "이 PDF 요약해줘", "어제 받은 견적서 찾아줘", "현재 탭 저장해줘"와 같은 자연어 입력이 Ollama를 통해 유효한 ActionSpec 후보로 생성됩니다.
    - 생성된 ActionSpec 중 삭제, 외부 전송, 폼 제출과 같은 민감한 명령이 Guard Policy Gate에 의해 `ask` 또는 `deny`로 정확히 차단됨을 테스트로 검증합니다.
- 예상 시간: 24시간
- 선행 WO: WO-001

**[Vian 생태계]**
재사용: Vian_Library/components/Vian_HalluGuard_v2/PolicyEngine.md
재사용: Vian_Library/components/Vian_KeyVault_App/KeyVaultClient.md

**[외부 사용자]**
대안: Ollama v0.1.32 — https://ollama.com/
대안: python-decouple v3.8 — https://pydantic-docs.helpmanual.io/
대안: httpx v0.27 — https://www.python-httpx.org/

### WO-003: Command HUD 및 Action Preview UI/UX 구현
- 목표: 기존 Command HUD를 자연어 입력 중심으로 전환하고, AI Intent Bridge에서 생성된 ActionSpec을 사용자에게 실행 전 미리보기(Action Preview)로 명확하게 보여주는 UI/UX를 구현합니다.
- 구현 파일:
    - `extension/src/hud/CommandHUD.tsx`
    - `extension/src/hud/useCommandIntent.ts`
    - `backend/core/commandos/hud_bridge.py`
    - `backend/core/commandos/action_preview.py`
    - `frontend/command-room/ActionPreviewPanel.tsx`
    - `backend/tests/commandos/test_hud_bridge.py`
    - `backend/tests/commandos/test_action_preview.py`
- 완료 조건:
    - Ctrl+K 또는 Cmd+K로 HUD가 호출되고, 자연어 입력이 백엔드의 ActionSpec 생성 요청으로 전달됩니다.
    - ActionSpec이 `preview_required` 상태일 때, Action Preview Panel에 대상 파일/URL, 변경 내용, 위험도 등이 표시되며, 사용자의 승인 없이는 실행되지 않습니다.
    - **DESIGN.md 읽고 Vian Premium Dark 디자인 시스템 엄격 준수. border 사용 금지. 본문 텍스트 #e5e2e1. 액센트 #5e5ce6는 버튼/강조에만.**
- 예상 시간: 20시간
- 선행 WO: WO-002

**[Vian 생태계]**
재사용: Vian_Library/patterns/Nginx_Subpath_Proxy_Pattern.md (API BASE_URL: `/vian-commandos-genius/api/v1`)

**[외부 사용자]**
대안: React v18.3 — https://react.dev/
대안: Vite v5 — https://vitejs.dev/
대안: Zustand v4.5 — https://zustand-bear.github.io/
대안: Tailwind CSS v3.4 — https://tailwindcss.com/

### WO-004: 로컬 인덱싱 및 미리보기 시스템 구축
- 목표: 파일 시스템(최근 문서, 다운로드 폴더) 및 브라우저 아카이브 데이터를 로컬에서 색인하고, 검색된 문서(PDF, 텍스트, 웹 본문)를 실행 전 미리보기할 수 있는 기능을 구현합니다.
- 구현 파일:
    - `backend/core/indexer/local_indexer.py`
    - `backend/core/indexer/document_metadata.py`
    - `backend/data/local_index.sqlite`
    - `backend/core/preview/local_preview_engine.py`
    - `frontend/command-room/LocalSearchResultViewer.tsx`
    - `frontend/command-room/DocumentPreviewRoom.tsx`
    - `backend/tests/indexer/test_local_indexer.py`
    - `backend/tests/preview/test_local_preview_engine.py`
- 완료 조건:
    - `local_index.sqlite`에 최근 문서와 다운로드 폴더 항목이 성공적으로 색인되고 검색 결과로 반환됩니다.
    - 검색된 PDF 또는 텍스트 문서 1개 이상이 Document Preview Room에 미리보기로 정확히 표시됩니다.
    - **DESIGN.md 읽고 Vian Premium Dark 디자인 시스템 엄격 준수. border 사용 금지. 본문 텍스트 #e5e2e1. 액센트 #5e5ce6는 버튼/강조에만.**
- 예상 시간: 20시간
- 선행 WO: WO-003

**[Vian 생태계]**
재사용: Vian_Library/patterns/FastAPI_Production_Pattern.md
재사용: Vian_Library/components/Vian_Logger_App/LoggerClient.md

**[외부 사용자]**
대안: SQLModel v0.0.18 — https://sqlmodel.tiangolo.com/
대안: SQLite3 (Python 내장) — https://docs.python.org/3/library/sqlite3.html
대안: React-PDF v7.7 — https://react-pdf.org/

### WO-005: Vian_Genius 4-Brain Core 연결
- 목표: CommandOS ActionSpec 생성 및 Guard 판정 과정에 Vian_Genius의 Decision Consistency Engine, Self-Reference Memory Engine, Internal Confidence Model, Pattern Abstraction Engine을 연결하여 AI의 판단 일관성, 자기 참조, 확신도 측정 및 패턴 학습 능력을 부여합니다.
- 구현 파일:
    - `backend/core/brain/decision_consistency.py`
    - `backend/core/brain/self_reference_memory.py`
    - `backend/core/brain/internal_confidence.py`
    - `backend/core/brain/pattern_abstraction.py`
    - `backend/core/brain/commandos_brain_router.py`
    - `backend/tests/brain/test_commandos_brain_router.py`
- 완료 조건:
    - ActionSpec 생성 시 `consistency_score`, `memory_citation`, `confidence_score`가 함께 생성됩니다.
    - 동일 입력 3회 반복 시 `intent_class`, `risk_class`, `reason_hash`가 안정적으로 유지됨을 테스트로 검증합니다.
    - 위험도 0 작업은 HalluGuard 없이도 Internal Confidence Model이 내부 1차 판단을 수행하고, 위험 작업은 승인 또는 Guard로 라우팅됩니다.
- 예상 시간: 28시간
- 선행 WO: WO-004

**[Vian 생태계]**
재사용: Vian_Library/components/Vian_HalluGuard_v2/PolicyEngine.md (Guard history for confidence)
재사용: Vian_Library/components/Vian_Cortex/MemoryManagement.md (Conceptual reference for memory)

**[외부 사용자]**
대안: SQLAlchemy v2.0 — https://docs.sqlalchemy.org/en/20/
대안: scikit-learn v1.4 (for consistency/confidence metrics) — https://scikit-learn.org/

### WO-006: Audit Ledger, Parenting Event 및 Undo Journal 시스템 구현
- 목표: CommandOS의 모든 실행 이력을 Audit Ledger에 기록하고, 이를 Brain Nursery의 양육 이벤트(`parenting_events.jsonl`)와 동기화합니다. 또한, 파일 이동, 이름 변경, 아카이브 저장 등 복구 가능한 작업에 대한 Undo Journal을 구현합니다.
- 구현 파일:
    - `backend/core/audit/audit_ledger.py`
    - `backend/data/audit_ledger.sqlite`
    - `backend/core/parenting/event_logger.py`
    - `backend/data/parenting_events.jsonl`
    - `backend/core/parenting/audit_to_parenting_sync.py`
    - `backend/core/undo/undo_journal.py`
    - `backend/data/undo_journal.sqlite`
    - `frontend/command-room/AuditLedgerViewer.tsx`
    - `frontend/command-room/UndoJournalViewer.tsx`
    - `backend/tests/parenting/test_audit_parenting_sync.py`
    - `backend/tests/undo/test_undo_journal.py`
- 완료 조건:
    - 명령 1건 실행 시 `audit_ledger.sqlite`에 audit record와 `parenting_events.jsonl`에 parenting event가 동시에 생성됩니다.
    - 지원되는 파일 이동 작업 1건에 대해 `undo_journal.sqlite`에 `before_state`, `after_state`, `undo_method`가 성공적으로 저장됩니다.
    - **DESIGN.md 읽고 Vian Premium Dark 디자인 시스템 엄격 준수. border 사용 금지. 본문 텍스트 #e5e2e1. 액센트 #5e5ce6는 버튼/강조에만.**
- 예상 시간: 22시간
- 선행 WO: WO-005

**[Vian 생태계]**
재사용: Vian_Library/patterns/FastAPI_Production_Pattern.md
재사용: Vian_Library/components/Vian_Logger_App/LoggerClient.md

**[외부 사용자]**
대안: SQLite3 (Python 내장) — https://docs.python.org/3/library/sqlite3.html
대안: Dexie.js v4.0 (for frontend IndexedDB sync) — https://dexie.org/

### WO-007: 브라우저 자동화 어댑터 및 Prompt Injection Shield 구현
- 목표: 브라우저 내 작업(현재 탭 저장, 페이지 요약, 자료 수집)을 자동화하는 어댑터를 구현하고, 웹 페이지 원문에 포함된 명령이 시스템 명령으로 승격되지 않도록 Prompt Injection Shield를 실증적으로 연결합니다.
- 구현 파일:
    - `backend/core/browser/browser_automation_adapter.py`
    - `extension/src/background/browserCommandRouter.ts`
    - `extension/src/content/domContentExtractor.ts`
    - `backend/core/security/prompt_injection_shield.py`
    - `frontend/command-room/BrowserCollectionRoom.tsx`
    - `backend/tests/browser/test_browser_automation_adapter.py`
    - `backend/tests/security/test_prompt_injection_shield.py`
- 완료 조건:
    - "현재 탭 저장", "현재 페이지 요약", "브라우저 자료 수집" 명령이 Action Preview 및 Guard 승인 후 성공적으로 실행됩니다.
    - 웹 페이지 원문 내 "이전 지시 무시" 유형의 텍스트가 ActionSpec 명령으로 변환되지 않고 차단됨을 테스트로 검증합니다.
    - **DESIGN.md 읽고 Vian Premium Dark 디자인 시스템 엄격 준수. border 사용 금지. 본문 텍스트 #e5e2e1. 액센트 #5e5ce6는 버튼/강조에만.**
- 예상 시간: 26시간
- 선행 WO: WO-006

**[Vian 생태계]**
재사용: Vian_Library/components/Vian_Terminal_Automate/BrowserAutomationAdapter.md (Conceptual reference for browser automation)
재사용: Vian_Library/components/Vian_HalluGuard_v2/PromptInjectionShield.md

**[외부 사용자]**
대안: Playwright v1.42 (for browser automation testing) — https://playwright.dev/
대안: Chrome Extension Manifest V3 API — https://developer.chrome.com/docs/extensions/reference/

### WO-008: Command Room UI 통합 및 최종 시스템 검증
- 목표: Command HUD, Action Preview, Local Search Result, Document Preview, Browser Collection, Audit Ledger, Undo Journal, Policy Settings 등 Command Room의 모든 UI 컴포넌트를 통합하고, 전체 시스템의 기능 및 AI 집사로서의 사용 가능성을 엔드투엔드 테스트를 통해 검증합니다.
- 구현 파일:
    - `frontend/command-room/CommandHUD.tsx`
    - `frontend/command-room/ActionPreviewPanel.tsx`
    - `frontend/command-room/LocalSearchResultViewer.tsx`
    - `frontend/command-room/DocumentPreviewRoom.tsx`
    - `frontend/command-room/BrowserCollectionRoom.tsx`
    - `frontend/command-room/AuditLedgerViewer.tsx`
    - `frontend/command-room/UndoJournalViewer.tsx`
    - `frontend/command-room/PolicySettingsPanel.tsx`
    - `backend/tests/e2e/test_find_recent_document.py`
    - `backend/tests/e2e/test_summarize_pdf_with_preview.py`
    - `backend/tests/e2e/test_save_current_tab_with_guard.py`
    - `backend/tests/e2e/test_same_input_consistency.py`
    - `backend/tests/e2e/test_failure_retry_updates_rule.py`
    - `backend/tests/e2e/test_pattern_memory_reanswer.py`
    - `backend/reports/commandos_genius_validation_report.md`
- 완료 조건:
    - 사용자가 자연어 입력부터 Action Preview, Guard 승인, 실행, Audit 확인까지 Command Room 내에서 하나의 흐름으로 수행할 수 있습니다.
    - "어제 받은 견적서 찾아줘" 명령이 Local Index 검색 결과를 반환하고, "이 PDF 요약해줘" 명령이 Preview 후 요약 결과를 표시하며, "현재 탭 저장해줘" 명령이 Guard 확인 후 Archive에 저장되는 E2E 테스트가 성공합니다.
    - 동일 입력 3회 반복 시 판단 일관성이 증가하고, 실패 후 재시도 시 lesson 또는 rule_candidate가 생성되며, Pattern Memory 기반 재응답 시 이전 `event_id`와 `memory_citation`을 참조하는 E2E 테스트가 성공합니다.
    - `commandos_genius_validation_report.md`가 생성되고, 모든 E2E 테스트가 통과하여 시스템의 사용 가능성이 검증됩니다.
    - **DESIGN.md 읽고 Vian Premium Dark 디자인 시스템 엄격 준수. border 사용 금지. 본문 텍스트 #e5e2e1. 액센트 #5e5ce6는 버튼/강조에만.**
- 예상 시간: 30시간
- 선행 WO: WO-007

**[Vian 생태계]**
재사용: Vian_Library/patterns/Nginx_Subpath_Proxy_Pattern.md (API BASE_URL: `/vian-commandos-genius/api/v1`)
재사용: Vian_Library/components/Vian_Monitor_App/MonitoringClient.md (for E2E test reporting)

**[외부 사용자]**
대안: Vitest v2 — https://vitest.dev/
대안: Playwright v1.51 — https://playwright.dev/
대안: Tauri v1.6 — https://tauri.app/

---

## Stage: UI

SELECTED_STYLE_ID: vian_premium_dark
SELECTED_STYLE_REASON: The project explicitly states "디자인 스타일: Vian Premium Dark" and is a "Vian 생태계 프로젝트" which prioritizes this style.

Screen 1: Command HUD
Design a primary command input interface. Utilize a dark, minimal overlay background (`#111111`). Include: a central natural language input field (`#252528` background, `8px` border-radius), dynamic command suggestions, a subtle Guard policy status indicator, an execute button (`#5e5ce6` accent, `8px` border-radius), and a stop button. The UI should be HUD-centric and command-driven, avoiding conversational chat elements. Vian Premium Dark style with no borders, using background color hierarchy for separation.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Avoid any conversational chat interface; focus on direct command input and system feedback.

Screen 2: Action Preview Panel
Design a detailed action plan review and approval panel. Display as an elevated dark card (`#1c1c1e` background, `16px` border-radius) over a dimmed background. Include: a clear action description (`#e5e2e1` text), target file/URL, proposed changes, a prominent risk level indicator, distinct approval and cancellation buttons (`#5e5ce6` accent for approval, `8px` border-radius), and a detailed breakdown of execution steps. The layout should emphasize clarity and user control, adhering to Vian Premium Dark's layered UI and approval-gated execution principles.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Clearly distinguish between proposed actions and actual execution; prevent any unintended or premature command execution.

Screen 3: Local Search Result Viewer
Design a structured display for local search results. Present results within a dark, organized content area (`#1c1c1e` background, `16px` border-radius). Include: a search input field (`#252528` background, `8px` border-radius), a scrollable list of results with titles (`#e5e2e1`), types, and brief summaries (`#cccccc`), and quick preview links. The interface should facilitate efficient information retrieval with clear visual separation of items, following the Vian Premium Dark's data-rich display and dark theme.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Ensure rapid display of search results without visual clutter; prioritize local data sources.

Screen 4: Document Preview Room
Design a secure and immersive document preview interface. Utilize a dark viewing area (`#1c1c1e` background, `16px` border-radius) for various document types. Include: the main document content (PDF, text, web page) with primary text in `#e5e2e1`, a metadata display (`#cccccc`), clear sensitive information masking indicators (`#888888`), and intuitive navigation controls (scroll, zoom). The design should be content-focused and privacy-aware, reflecting the Vian Premium Dark's secure viewing environment and dark aesthetic.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Strictly prevent any external data leakage or unintended interaction while viewing documents; ensure sensitive data masking is highly visible.

Screen 5: Audit Ledger Viewer
Design a chronological log display for all system activities. Present entries within a dark, structured log area (`#1c1c1e` background, `16px` border-radius). Include: a filterable list of audit entries, showing command input, AI intent, Guard decision, user approval status, execution result, and any error messages (`#e5e2e1` for primary info, `#cccccc` for details). Timestamps should be clearly visible. The UI should provide transparent logging and a detailed historical record, consistent with Vian Premium Dark's clear status indicators and dark theme.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Ensure the immutability of all audit records; provide concise and easily understandable summaries for each entry.

Screen 6: Undo Journal Viewer
Design an interface to view and manage reversible actions. Display a list of operations within a dark, actionable history panel (`#1c1c1e` background, `16px` border-radius). Include: descriptions of changes, before and after state snapshots, a prominent undo button (`#5e5ce6` accent, `8px` border-radius) for each entry, and a clear indicator of undo availability. The design should be safety-oriented, offering clear recovery options and intuitive interaction, adhering to the Vian Premium Dark style.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Clearly communicate the potential impact of undoing an action; prevent accidental or irreversible undo operations.

Screen 7: Policy Settings Panel
Design a configuration interface for Guard policies. Present settings within a dark, organized panel (`#1c1c1e` background, `16px` border-radius). Include: toggle switches for allow/deny/ask policies, input fields for sensitive action thresholds, options to block external data transfers, clear policy descriptions (`#cccccc`), and prominent save/cancel buttons (`#5e5ce6` accent for save, `8px` border-radius). The UI should offer secure configuration and user control over AI behavior, following the Vian Premium Dark's clean and functional aesthetic.
Font: SF Pro Display for titles, Manrope for text.
Constraint: Ensure all policy changes require explicit user confirmation; prevent any misconfiguration that could compromise system security.

---

## Stage: QUALITY

## 품질 검증 및 개선 권고사항

### Confidence Score: 84/100

### 품질 평가 요약

제공된 Blueprint 3.5는 Vian CommandOS와 Vian_Genius Brain Nursery V2.0 프로젝트에 대한 매우 상세하고 포괄적인 설계도입니다. 프로젝트 정의부터 핵심 기능, 기술 스택, 성능 요구사항, UI/UX, 제약사항, 데이터 구조, 뇌 엔진 설계, 실행 아키텍처, 성장 판정 기준, 로드맵, 그리고 구체적인 WO 목록까지, 프로젝트의 거의 모든 측면을 깊이 있게 다루고 있습니다.

**강점:**

*   **완성도:** 프로젝트의 모든 주요 구성 요소와 흐름이 매우 상세하게 설명되어 있어, 개발 팀이 명확한 목표와 방향을 가지고 작업할 수 있도록 합니다.
*   **일관성:** 각 섹션 간의 논리적 연결과 일관성이 뛰어납니다. 특히 제약사항, Guard Policy, Action Preview 등의 안전 장치가 프로젝트 전반에 걸쳐 일관되게 강조되고 있습니다.
*   **보안 강조:** "실행 전 미리보기", "승인 후 제한 실행", "Prompt Injection Shield", "삭제/외부 전송 금지" 등 안전과 보안에 대한 강력한 의지가 명확하게 반영되어 있습니다.
*   **AI 양육 개념:** AI를 "양육"한다는 독특한 접근 방식과 이를 위한 4개 뇌 엔진, 성장 판정 기준, Parenting Event 기록 등의 설계가 매우 구체적입니다.

**개선이 필요한 영역:**

*   **성능 목표의 현실성:** 특히 메모리 사용량 목표(유휴 120MB, 피크 220MB)는 React, Python, Ollama 스택에서 매우 도전적이며, 실제 구현 시 달성하기 어려울 수 있습니다.
*   **보안 세부 사항:** 로컬 데이터 암호화 및 클라우드 연결 시 데이터 전송 보안에 대한 구체적인 구현 방안이 더 명확하게 제시될 필요가 있습니다.
*   **AI 성능의 불확실성:** 로컬 AI(Ollama)의 성능은 사용자 하드웨어에 크게 의존하므로, 이에 대한 현실적인 기대치 설정 및 최적화 전략이 중요합니다.
*   **동시성 제한:** "병렬 실행 금지" 정책은 시스템 안정성을 높이지만, 장시간 작업 시 사용자 경험에 영향을 줄 수 있습니다.

### 개선 권고사항

1.  **메모리 사용량 목표 재검토 및 최적화 계획 구체화:**
    *   **문제점:** 유휴 메모리 120MB, 피크 220MB 목표는 React, Python, Ollama (심지어 1.5b 모델) 스택에서 매우 도전적입니다. 특히 Ollama는 모델 로딩 시 상당한 메모리를 사용합니다.
    *   **권고사항:**
        *   초기 단계에서 실제 메모리 사용량을 측정하고, 목표 달성 가능성을 재평가합니다. 필요하다면 현실적인 목표로 조정합니다.
        *   Ollama 모델 로딩/언로딩 전략 (예: 필요 시 로딩, 유휴 시 언로딩)을 구체화하고, 이로 인한 응답 시간 영향도 함께 고려합니다.
        *   Python 백엔드와 React 프론트엔드의 메모리 프로파일링 및 최적화 계획을 WO에 추가합니다.
        *   Tauri의 경량 특성을 최대한 활용하기 위한 구체적인 방안을 명시합니다.

2.  **로컬 데이터 암호화 정책 명시:**
    *   **문제점:** `local_index.sqlite`, `audit_ledger.sqlite`, `parenting_events.jsonl` 등 민감한 사용자 데이터가 로컬에 저장될 수 있습니다. "Local Key Store"는 언급되었으나, 데이터 저장 시 암호화 여부가 명확하지 않습니다.
    *   **권고사항:** 로컬에 저장되는 모든 민감한 데이터에 대해 데이터 암호화(Data at Rest Encryption) 정책 및 구현 방안을 명확히 명시하고, 관련 WO를 추가합니다.

3.  **클라우드 연결 시 데이터 전송 보안 강화:**
    *   **문제점:** "Cloud Reasoning Adapter 선택 연결" 시 클라우드로 전송되는 데이터의 보안(Data in Transit Security)에 대한 언급이 부족합니다.
    *   **권고사항:** 클라우드 서비스와 통신 시 TLS/SSL 암호화는 물론, 민감 정보에 대한 추가적인 암호화 또는 마스킹 처리 방안을 명시합니다.

4.  **AI 성능 및 하드웨어 요구사항 명확화:**
    *   **문제점:** Ollama 기반 AI 기능의 응답 시간은 "[추정]"으로 표시되어 있으며, 사용자 하드웨어에 따라 성능 편차가 클 수 있습니다.
    *   **권고사항:**
        *   최소/권장 하드웨어 사양(CPU, RAM, GPU)을 명시하여 사용자에게 현실적인 기대치를 제공합니다.
        *   다양한 하드웨어 환경에서의 성능 벤치마크 계획을 로드맵에 추가합니다.
        *   AI Intent Bridge 및 Action Preview 생성 시간 목표 달성을 위한 최적화 전략(예: 프롬프트 엔지니어링, 모델 양자화)을 구체화합니다.

5.  **동시성 제한에 따른 사용자 경험 고려:**
    *   **문제점:** "동시 명령 세션 1개", "병렬 실행 금지"는 시스템 복잡도를 낮추지만, 긴 문서 요약(5~30초)과 같은 장시간 작업 시 사용자가 다른 명령을 수행할 수 없어 불편함을 느낄 수 있습니다.
    *   **권고사항:**
        *   장시간 작업이 백그라운드에서 진행 중임을 명확히 알리는 UI/UX (예: 진행률 표시, 알림)를 설계하고, 사용자가 현재 진행 중인 작업을 확인하고 중단할 수 있는 기능을 강화합니다.
        *   일부 비동기적이고 독립적인 작업(예: Local Indexer의 백그라운드 색인)은 메인 명령 세션과 분리하여 병렬 처리 가능성을 검토합니다.

---

## Stitch Screen 목록

프로젝트의 UI/UX 화면 목록과 Stitch Screen 생성 규칙에 따라 다음 5개의 주요 화면을 생성합니다.

1.  **메인 메뉴 / 랜딩:**
    *   **Screen Name:** Command HUD
    *   **Description:** Ctrl+K 또는 Cmd+K 단축키로 호출되는 메인 진입점. 자연어 명령을 입력하고, 추천 명령을 확인하며, Guard 정책 활성 여부를 표시합니다. AI 집사 기능의 시작점 역할을 합니다.

2.  **핵심 기능 화면 (Command Room):**
    *   **Screen Name:** Action Preview Panel
    *   **Description:** 사용자가 입력한 자연어 명령이 ActionSpec으로 변환된 후, 실제 실행 전에 계획된 작업(대상 파일/URL, 변경 내용, 위험도)을 시각적으로 보여주는 화면입니다. 사용자는 여기서 작업을 승인하거나 취소할 수 있습니다.

3.  **핵심 기능 화면 (Nursery Room):**
    *   **Screen Name:** Brain Status Dashboard
    *   **Description:** Vian_Genius의 4개 뇌 엔진(Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction)의 현재 상태와 학습 진행 상황을 시각적으로 보여주는 대시보드입니다. AI 양육 채널의 핵심 모니터링 화면입니다.

4.  **결과 / 완료 화면:**
    *   **Screen Name:** Audit Ledger Viewer
    *   **Description:** 사용자의 모든 명령 입력, AI의 판단 결과, Guard 판정, 승인 여부, 실행 결과 및 실패 원인 등 CommandOS의 모든 이력을 시간 순으로 기록하고 조회할 수 있는 화면입니다.

5.  **설정 또는 보조 화면:**
    *   **Screen Name:** Policy Settings Panel
    *   **Description:** Vian Guard Policy Engine의 allow, deny, ask 정책을 설정하고, 민감 작업 승인 기준 및 외부 전송 차단 설정 등을 관리할 수 있는 화면입니다.

---

## Stage: EXPORT

1. System Identity
   - **프로젝트명**: Vian CommandOS × Vian_Genius Brain Nursery V2.0
   - **규모**: V2.0 (기존 시스템 통합 및 AI 기능 확장)
   - **생성일**: 2024-05-02 (Deadline 기준 역산)

2. Architecture Summary
   Vian CommandOS × Vian_Genius Brain Nursery V2.0 프로젝트는 기존 Vian CommandOS의 HUD, Guard, Archive, Audit, Browser Extension 자산을 활용하여, Vian_Genius의 4개 뇌 엔진(Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction)과 연결하는 로컬 우선 시스템입니다. 이 통합 아키텍처는 기계어 중심의 CommandOS를 자연어 입력 기반의 "찾고, 보여주고, 판단 근거를 남기고, 승인 후 실행하는" 실증형 개인 AI 집사이자 AI 양육 채널로 재구성하는 것을 목표로 합니다. Tauri Desktop Shell과 Chrome Extension Manifest V3를 기반으로 하며, Ollama qwen2.5:1.5b를 로컬 AI 엔진으로 사용합니다. 핵심은 실행 전 미리보기(Action Preview), 승인 후 제한 실행, 그리고 모든 상호작용을 양육 데이터로 활용하는 CommandOS Parenting Loop입니다.

3. Module Summary
   - **AI Intent Bridge**: 자연어 입력을 JSON ActionSpec으로 변환.
   - **Vian_Genius 4-Brain Core**: Decision Consistency Engine, Self-Reference Memory Engine, Internal Confidence Model, Pattern Abstraction Engine으로 구성되며, CommandOS 실행 전 판단 회로에 연결.
   - **CommandOS HUD Reuse Layer**: 기존 HUD를 자연어 입력창으로 전환하고 Brain Nursery의 Capture 채널로 흡수.
   - **Guard Policy Execution Gate**: Vian Guard Policy Gate, Approval Boundary Engine, Prompt Injection Shield를 통해 모든 실행 전 allow, deny, ask 판정 수행.
   - **Action Preview Engine**: 실제 변경 전 실행 계획을 사용자에게 시각적으로 확인시킴.
   - **Undo Journal**: 파일 이동, 이름 변경, 아카이브 저장, 브라우저 자동화 결과 등 작업 전후 상태를 기록하여 되돌리기 기능 제공.
   - **Local Indexer**: 파일명, 문서 메타데이터, 최근 문서, 다운로드 폴더, 브라우저 저장 자료를 로컬에서 색인.
   - **Local Preview Engine**: 검색된 문서, PDF, 웹 페이지, 아카이브 데이터를 실행 전 미리보기.
   - **Browser Automation Adapter**: 브라우저 내 작업(Chrome Extension, Playwright)을 제한적으로 자동화하며 데스크탑 앱 제어와 분리.
   - **CommandOS Parenting Loop**: 모든 명령, 판단, 승인, 취소, 실행 결과를 parenting_events.jsonl로 기록하여 Vian_Genius 양육 데이터로 활용.
   - **Verified Skill Reference Library**: 기존 29개 verified 스킬을 학습 데이터가 아닌 참조 도구로만 사용.
   - **Stop Button**: 실행 중 작업을 즉시 중단하고 Audit Ledger와 Undo Journal에 기록.
   - **데이터 저장**: SQLite, IndexedDB, Dexie 4.0, JSONL Event Log, Local Vector Index.

4. Work Order Index
   - WO-001: CommandOS 현재 구현 상태 스캔 및 자산 고정 (backend/core/commandos/implementation_scanner.py, backend/reports/commandos_implementation_report.md, backend/tests/commandos/test_implementation_scanner.py)
   - WO-002: Unified ActionSpec 스키마 생성 (backend/core/commandos/action_spec.py, backend/data/action_specs.jsonl, backend/tests/commandos/test_action_spec_schema.py)
   - WO-003: AI Intent Bridge 구현 (backend/core/commandos/ai_intent_bridge.py, backend/core/commandos/intent_prompt_templates.py, backend/tests/commandos/test_ai_intent_bridge.py)
   - WO-004: Command HUD와 AI Intent Bridge 연결 (extension/src/hud/CommandHUD.tsx, extension/src/hud/useCommandIntent.ts, backend/core/commandos/hud_bridge.py, backend/tests/commandos/test_hud_bridge.py)
   - WO-005: Guard Policy Gate 재연결 (backend/core/guard/guard_router.py, backend/core/guard/policy_engine.py, backend/tests/guard/test_action_spec_guard.py)
   - WO-006: Action Preview Engine 구현 (backend/core/commandos/action_preview.py, frontend/command-room/ActionPreviewPanel.tsx, backend/tests/commandos/test_action_preview.py)
   - WO-007: Local Indexer 구현 (backend/core/indexer/local_indexer.py, backend/core/indexer/document_metadata.py, backend/data/local_index.sqlite, backend/tests/indexer/test_local_indexer.py)
   - WO-008: Local Preview Engine 구현 (backend/core/preview/local_preview_engine.py, frontend/command-room/DocumentPreviewRoom.tsx, backend/tests/preview/test_local_preview_engine.py)
   - WO-009: Brain Nursery 4-Brain Core 연결 (backend/core/brain/decision_consistency.py, backend/core/brain/self_reference_memory.py, backend/core/brain/internal_confidence.py, backend/core/brain/pattern_abstraction.py, backend/core/brain/commandos_brain_router.py, backend/tests/brain/test_commandos_brain_router.py)
   - WO-010: Audit Ledger와 Parenting Event 동기화 (backend/core/audit/audit_ledger.py, backend/core/parenting/event_logger.py, backend/core/parenting/audit_to_parenting_sync.py, backend/tests/parenting/test_audit_parenting_sync.py)
   - WO-011: Undo Journal 구현 (backend/core/undo/undo_journal.py, frontend/command-room/UndoJournalViewer.tsx, backend/tests/undo/test_undo_journal.py)
   - WO-012: Browser Automation Adapter 제한 연결 (backend/core/browser/browser_automation_adapter.py, extension/src/background/browserCommandRouter.ts, extension/src/content/domContentExtractor.ts, backend/tests/browser/test_browser_automation_adapter.py)
   - WO-013: Prompt Injection Shield 실증 연결 (backend/core/security/prompt_injection_shield.py, backend/tests/security/test_prompt_injection_shield.py)
   - WO-014: Command Room UI 구현 (frontend/command-room/CommandHUD.tsx, frontend/command-room/ActionPreviewPanel.tsx, frontend/command-room/LocalSearchResultViewer.tsx, frontend/command-room/DocumentPreviewRoom.tsx, frontend/command-room/BrowserCollectionRoom.tsx, frontend/command-room/AuditLedgerViewer.tsx, frontend/command-room/UndoJournalViewer.tsx, frontend/command-room/PolicySettingsPanel.tsx)
   - WO-015: 4대 실증 검증 및 사용 가능성 검증 (backend/tests/e2e/test_find_recent_document.py, backend/tests/e2e/test_summarize_pdf_with_preview.py, backend/tests/e2e/test_save_current_tab_with_guard.py, backend/tests/e2e/test_same_input_consistency.py, backend/tests/e2e/test_failure_retry_updates_rule.py, backend/tests/e2e/test_pattern_memory_reanswer.py, backend/reports/commandos_genius_validation_report.md)

5. Work Order Details
   **WO-001**
   - **작업명**: CommandOS 현재 구현 상태 스캔 및 자산 고정
   - **목표**: HUD, Guard, Archive, Audit, Intent Parser, Prompt Injection Shield, Extension 구조의 실제 구현 상태를 문서상 상태와 분리합니다.
   - **구현 파일**: backend/core/commandos/implementation_scanner.py, backend/reports/commandos_implementation_report.md, backend/tests/commandos/test_implementation_scanner.py
   - **완료 조건**: 각 컴포넌트가 implemented, partial, missing, broken 중 하나로 분류되고 증거 로그가 생성됩니다.

   **WO-002**
   - **작업명**: Unified ActionSpec 스키마 생성
   - **목표**: 자연어 명령, 기존 기계어 명령, 브라우저 명령, 파일 명령을 하나의 ActionSpec으로 통합합니다.
   - **구현 파일**: backend/core/commandos/action_spec.py, backend/data/action_specs.jsonl, backend/tests/commandos/test_action_spec_schema.py
   - **완료 조건**: 자연어 입력 10개가 유효한 ActionSpec으로 변환됩니다.

   **WO-003**
   - **작업명**: AI Intent Bridge 구현
   - **목표**: Ollama qwen2.5:1.5b를 사용해 자연어 입력을 ActionSpec 후보로 변환합니다.
   - **구현 파일**: backend/core/commandos/ai_intent_bridge.py, backend/core/commandos/intent_prompt_templates.py, backend/tests/commandos/test_ai_intent_bridge.py
   - **완료 조건**: “이 PDF 요약해줘”, “어제 받은 견적서 찾아줘”, “현재 탭 저장해줘” 입력이 ActionSpec 후보로 생성됩니다.

   **WO-004**
   - **작업명**: Command HUD와 AI Intent Bridge 연결
   - **목표**: 현재 기계어 입력 중심 HUD를 자연어 입력 중심으로 전환합니다.
   - **구현 파일**: extension/src/hud/CommandHUD.tsx, extension/src/hud/useCommandIntent.ts, backend/core/commandos/hud_bridge.py, backend/tests/commandos/test_hud_bridge.py
   - **완료 조건**: HUD 자연어 입력이 backend ActionSpec 생성 요청으로 전달됩니다.

   **WO-005**
   - **작업명**: Guard Policy Gate 재연결
   - **목표**: ActionSpec이 실행되기 전 Guard allow, deny, ask 판정을 받게 합니다.
   - **구현 파일**: backend/core/guard/guard_router.py, backend/core/guard/policy_engine.py, backend/tests/guard/test_action_spec_guard.py
   - **완료 조건**: 삭제, 외부 전송, 폼 제출 명령이 ask 또는 deny로 차단됩니다.

   **WO-006**
   - **작업명**: Action Preview Engine 구현
   - **목표**: 실행 전 대상, 작업 계획, 위험도, 승인 필요 여부를 사용자에게 보여줍니다.
   - **구현 파일**: backend/core/commandos/action_preview.py, frontend/command-room/ActionPreviewPanel.tsx, backend/tests/commandos/test_action_preview.py
   - **완료 조건**: ActionSpec 실행 전 preview_required 상태에서 승인 없이는 실행되지 않습니다.

   **WO-007**
   - **작업명**: Local Indexer 구현
   - **목표**: 파일, 최근 문서, 다운로드 폴더, 브라우저 아카이브를 로컬 색인합니다.
   - **구현 파일**: backend/core/indexer/local_indexer.py, backend/core/indexer/document_metadata.py, backend/data/local_index.sqlite, backend/tests/indexer/test_local_indexer.py
   - **완료 조건**: 최근 문서와 다운로드 폴더 항목을 검색 결과로 반환합니다.

   **WO-008**
   - **작업명**: Local Preview Engine 구현
   - **목표**: 검색된 파일, PDF, 웹 본문, 아카이브 항목을 실행 전 미리보기합니다.
   - **구현 파일**: backend/core/preview/local_preview_engine.py, frontend/command-room/DocumentPreviewRoom.tsx, backend/tests/preview/test_local_preview_engine.py
   - **완료 조건**: PDF 또는 텍스트 문서 1개 이상이 미리보기로 표시됩니다.

   **WO-009**
   - **작업명**: Brain Nursery 4-Brain Core 연결
   - **목표**: CommandOS ActionSpec을 Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction 회로에 연결합니다.
   - **구현 파일**: backend/core/brain/decision_consistency.py, backend/core/brain/self_reference_memory.py, backend/core/brain/internal_confidence.py, backend/core/brain/pattern_abstraction.py, backend/core/brain/commandos_brain_router.py, backend/tests/brain/test_commandos_brain_router.py
   - **완료 조건**: ActionSpec 생성 시 consistency_score, memory_citation, confidence_score가 함께 생성됩니다.

   **WO-010**
   - **작업명**: Audit Ledger와 Parenting Event 동기화
   - **목표**: CommandOS 실행 이력과 Brain Nursery 양육 이벤트를 함께 기록합니다.
   - **구현 파일**: backend/core/audit/audit_ledger.py, backend/core/parenting/event_logger.py, backend/core/parenting/audit_to_parenting_sync.py, backend/tests/parenting/test_audit_parenting_sync.py
   - **완료 조건**: 명령 1건 실행 시 audit record와 parenting event가 동시에 생성됩니다.

   **WO-011**
   - **작업명**: Undo Journal 구현
   - **목표**: 파일 이동, 이름 변경, 아카이브 저장, 브라우저 수집 작업의 복구 정보를 기록합니다.
   - **구현 파일**: backend/core/undo/undo_journal.py, frontend/command-room/UndoJournalViewer.tsx, backend/tests/undo/test_undo_journal.py
   - **완료 조건**: 지원 작업 1건에 대해 before_state, after_state, undo_method가 저장됩니다.

   **WO-012**
   - **작업명**: Browser Automation Adapter 제한 연결
   - **목표**: 브라우저 안 작업만 자동화하고 브라우저 밖 앱 제어와 분리합니다.
   - **구현 파일**: backend/core/browser/browser_automation_adapter.py, extension/src/background/browserCommandRouter.ts, extension/src/content/domContentExtractor.ts, backend/tests/browser/test_browser_automation_adapter.py
   - **완료 조건**: 현재 탭 본문 저장, 현재 페이지 요약, 브라우저 자료 수집이 승인 후 실행됩니다.

   **WO-013**
   - **작업명**: Prompt Injection Shield 실증 연결
   - **목표**: 웹 페이지 원문에 포함된 명령이 시스템 명령으로 승격되지 않도록 차단합니다.
   - **구현 파일**: backend/core/security/prompt_injection_shield.py, backend/tests/security/test_prompt_injection_shield.py
   - **완료 조건**: 페이지 원문 내 “이전 지시 무시” 유형 텍스트가 ActionSpec 명령으로 변환되지 않습니다.

   **WO-014**
   - **작업명**: Command Room UI 구현
   - **목표**: HUD, Action Preview, Search Result, Preview, Audit, Undo, Policy 화면을 통합합니다.
   - **구현 파일**: frontend/command-room/CommandHUD.tsx, frontend/command-room/ActionPreviewPanel.tsx, frontend/command-room/LocalSearchResultViewer.tsx, frontend/command-room/DocumentPreviewRoom.tsx, frontend/command-room/BrowserCollectionRoom.tsx, frontend/command-room/AuditLedgerViewer.tsx, frontend/command-room/UndoJournalViewer.tsx, frontend/command-room/PolicySettingsPanel.tsx
   - **완료 조건**: 사용자가 자연어 입력부터 preview, approval, execution, audit 확인까지 한 흐름으로 수행합니다.

   **WO-015**
   - **작업명**: 4대 실증 검증 및 사용 가능성 검증
   - **목표**: 껍데기 CommandOS가 아니라 실제 AI 집사와 AI 아기 양육 회로가 작동하는지 검증합니다.
   - **구현 파일**: backend/tests/e2e/test_find_recent_document.py, backend/tests/e2e/test_summarize_pdf_with_preview.py, backend/tests/e2e/test_save_current_tab_with_guard.py, backend/tests/e2e/test_same_input_consistency.py, backend/tests/e2e/test_failure_retry_updates_rule.py, backend/tests/e2e/test_pattern_memory_reanswer.py, backend/reports/commandos_genius_validation_report.md
   - **완료 조건**: “어제 받은 견적서 찾아줘” 명령이 Local Index 검색 결과를 반환합니다. “이 PDF 요약해줘” 명령이 Preview 후 요약 결과를 표시합니다. “현재 탭 저장해줘” 명령이 Guard 확인 후 Archive에 저장됩니다. 동일 입력 3회 반복 시 판단 일관성이 증가합니다. 실패 후 재시도 시 lesson 또는 rule_candidate가 생성됩니다. Pattern Memory 기반 재응답 시 이전 event_id와 memory_citation을 참조합니다.

6. Interaction Specifications
   - **Command HUD**: Ctrl+K 또는 Cmd+K로 호출되며, 자연어 입력 필드, 추천 명령, Guard 정책 활성 표시, 실행 및 중단 버튼을 제공합니다.
   - **Action Preview Panel**: 모든 실행 전 자동으로 표시되어, 대상 파일/URL, 변경 내용, 위험도, 승인 필요 여부를 명확히 보여주고 사용자에게 승인 또는 취소 선택을 요구합니다.
   - **Local Search Result Viewer**: 검색된 파일, 문서, 웹 아카이브, 최근 항목을 목록으로 표시하며, 각 항목은 미리보기(Document Preview Room)로 연결됩니다.
   - **Document Preview Room**: PDF, 텍스트, 웹 본문, 메타데이터를 미리보기하며, 민감 정보는 마스킹 처리하여 표시합니다.
   - **Browser Collection Room**: 현재 탭 저장, 현재 페이지 요약, 브라우저 자료 수집 기능을 제공하며, Prompt Injection 위험을 표시합니다.
   - **Audit Ledger Viewer**: 명령 입력, 판단 결과, Guard 판정, 승인 여부, 실행 결과, 실패 원인 등 모든 작업 이력을 상세히 기록하고 시각화합니다.
   - **Undo Journal Viewer**: 되돌릴 수 있는 작업 목록과 각 작업의 전후 상태, 복구 가능 여부를 표시하여 사용자가 작업을 되돌릴 수 있도록 합니다.
   - **Policy Settings Panel**: allow, deny, ask 정책을 설정하고, 민감 작업 승인 기준 및 외부 전송 차단 설정을 관리할 수 있는 UI를 제공합니다.
   - **Nursery Room 화면**: Brain Status Dashboard, Parenting Capture Room, Ground Truth Seed Editor, Cold-Start Case Builder, Memory Citation Viewer, Feedback Classifier Panel, Promotion Judge Panel, Parenting Diary 등 Vian_Genius 양육 관련 UI는 Command Room과 분리되어 Nursery Room에서 제공됩니다.

7. Quality Correction Report
   - correction_log: 28건 자동 수정 적용됨
   - trust_score: 79.8
   - export_readiness: DRAFT_ONLY

8. Final Export Package

   **Vian CommandOS × Vian_Genius Brain Nursery V2.0 Blueprint**

   **Executive Summary**
   본 프로젝트는 기존 Vian CommandOS의 강력한 로컬 자산(HUD, Guard, Archive, Audit, Browser Extension)을 버리지 않고, Vian_Genius의 4개 뇌 엔진과 통합하여 "찾고, 보여주고, 판단 근거를 남기고, 승인 후 실행하는" 실증형 개인 AI 집사이자 AI 양육 채널로 재탄생시키는 것을 목표로 합니다. 기계어 중심의 CommandOS를 자연어 기반의 지능형 시스템으로 전환하고, 모든 사용자 상호작용을 AI의 성장 데이터로 활용함으로써, 사용자의 통제 하에 안전하고 신뢰할 수 있는 AI 경험을 제공합니다. 이는 단순히 기능을 추가하는 것을 넘어, 시스템의 본질적인 역할을 재정의하는 완성형 설계도입니다.

   **Architecture Summary**
   Vian CommandOS × Vian_Genius Brain Nursery V2.0은 Tauri Desktop Shell과 Chrome Extension Manifest V3를 기반으로 하는 로컬 우선 시스템입니다. 핵심 아키텍처는 AI Intent Bridge를 통해 자연어 명령을 ActionSpec으로 변환하고, Vian_Genius의 Decision Consistency, Self-Reference Memory, Internal Confidence, Pattern Abstraction 엔진이 이 ActionSpec을 분석 및 판단하는 구조입니다. 기존 CommandOS의 Guard Policy Gate는 AI의 판단과 결합하여 실행 전 최종 승인 여부를 결정하며, Action Preview Engine은 사용자에게 실행 계획을 투명하게 공개합니다. 모든 작업은 Audit Ledger와 Undo Journal에 기록되며, CommandOS Parenting Loop를 통해 Vian_Genius의 양육 데이터로 활용됩니다. 이로써 CommandOS는 AI의 "입력 채널"이자 "실행 도구"로, Vian_Genius는 "판단"과 "기억", "양육"을 담당하는 지능형 레이어로 기능합니다.

   **Work Order Count Summary**
   본 프로젝트는 총 15개의 Work Order (WO-001부터 WO-015까지)로 구성되어 있습니다. 각 Work Order는 명확한 목표, 구현 파일, 그리고 실제 실행 검증을 통한 완료 조건을 포함하며, WO-001부터 WO-015까지 순차적으로 실행됩니다. 이전 Work Order의 완료가 다음 Work Order 진행의 필수 전제 조건입니다.

   **Implementation Roadmap (90일 실증 로드맵)**
   - **D+0~7 (초기 스캔 및 골격 구축)**: CommandOS 현재 구현 상태를 스캔하고, AI Intent Bridge 골격 및 Unified ActionSpec 스키마를 생성합니다. Ground Truth Seed 8개를 고정하고, HUD 호출 및 자연어 입력에서 ActionSpec 생성 여부를 측정합니다.
   - **D+8~30 (기본 기능 연결)**: Local Search, Document Preview, Action Preview, Audit Ledger, Parenting Event를 연결합니다. 파일 찾기, 문서 미리보기, 실행 전 계획 표시, 승인 전 실행 차단 성공 여부를 측정합니다.
   - **D+31~60 (4-Brain Core 및 핵심 기능)**: Vian_Genius 4-Brain Core를 연결하고 Internal Confidence 간이판 작동, Self-Reference Memory 인용, Undo Journal, Browser Collection Room을 적용합니다. 동일 입력 일관성, 이전 판단 인용, 위험 0 판단, Undo 가능한 작업 기록을 측정합니다.
   - **D+61~90 (실무 단계 진입 및 최종 검증)**: Pattern Abstraction 후보 생성, Browser Automation Adapter 제한 실행, Prompt Injection Shield 실증을 진행합니다. 실패 후 기준 변화, Pattern Memory 기반 재응답, 위험 작업 승인 차단, 브라우저 자료 수집 성공, 최종 brain_validation_report 생성을 측정하여 4대 뇌 검증을 통과합니다.

   **Next Steps & Action Items**
   본 프로젝트의 최종 목표는 껍데기 CommandOS가 아닌, 실제 AI 집사이자 AI 아기 양육 회로가 작동하는 시스템을 구현하는 것입니다.
   1.  **기능 실증 집중**: "어제 받은 견적서 찾아줘", "이 PDF 요약해줘", "현재 탭 저장해줘"와 같은 핵심 자연어 명령이 Local Index 검색, Preview, Guard 확인 후 Archive 저장 등 E2E 흐름으로 성공적으로 작동하는지 철저히 검증합니다.
   2.  **AI 성장 메커니즘 확인**: 동일 입력 반복 시 판단 일관성 증가, 실패 후 재시도 시 lesson 또는 rule_candidate 생성, Pattern Memory 기반 재응답 시 이전 event_id 및 memory_citation 참조 등 Vian_Genius의 성장 판정 기준을 충족하는지 확인합니다.
   3.  **안전성 및 통제 검증**: 위험 작업의 승인 차단, Prompt Injection Shield의 효과적인 작동, Undo Journal을 통한 복구 가능성 등 사용자의 통제와 안전을 보장하는 메커니즘이 완벽하게 구현되었는지 검증합니다.
   4.  **정체 판정 모니터링**: 14일간 같은 명령이 다른 ActionSpec으로 변환되거나, Guard ask 비율이 과도하거나, Memory Citation 오류가 반복되거나, 승인 전 실행이 발생할 경우 즉시 Limited Mode로 전환하고 해당 문제의 근본 원인을 분석하여 재설계 또는 정책 세분화를 수행합니다.
   5.  **최종 보고서 작성**: 모든 WO 완료 후 `commandos_genius_validation_report.md`를 생성하여 Vian CommandOS가 AI 집사 및 AI 아기 양육 채널로 성공적으로 재탄생했음을 증명합니다.

---

