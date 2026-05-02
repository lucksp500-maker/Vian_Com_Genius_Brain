/**
 * PolicySettingsPanel — WO-008
 * Guard 정책 설정 UI.
 * allow / deny / ask 기준, 민감 작업 승인 설정, 외부 전송 차단 설정.
 *
 * 흐름:
 *   GET /api/v1/guard/policy → 현재 정책 표시
 *   사용자 토글 → POST /api/v1/guard/policy (설정 저장)
 *
 * V1 범위:
 *   정책 표시 + 고위험 작업 설명 + 기본값 안내
 *   실제 저장 API는 V2에서 확장 (V1 = 읽기 전용 표시)
 *
 * [의존성] 연결: Guard PolicyEngine / 단독 수정 금지
 */
import { useState } from 'react'

// ─── 타입 ───────────────────────────────────────────────────────

interface PolicyRule {
  id: string
  label: string
  description: string
  currentValue: 'allow' | 'deny' | 'ask'
  locked: boolean  // V1 = 변경 불가 (안전 기본값)
}

// ─── 기본 정책 규칙 (Guard PolicyEngine 기반) ────────────────────

const DEFAULT_RULES: PolicyRule[] = [
  {
    id: 'file_delete',
    label: '파일 삭제',
    description: '파일을 삭제하는 명령 — V1에서 기본 금지',
    currentValue: 'deny',
    locked: true,
  },
  {
    id: 'external_send',
    label: '외부 전송',
    description: '데이터를 외부 서버로 전송하는 명령 — V1에서 기본 금지',
    currentValue: 'deny',
    locked: true,
  },
  {
    id: 'high_risk_action',
    label: '고위험 작업',
    description: 'risk_level=high로 분류된 명령 — 반드시 사용자 승인 필요',
    currentValue: 'ask',
    locked: true,
  },
  {
    id: 'medium_risk_action',
    label: '중간위험 작업',
    description: 'risk_level=medium으로 분류된 명령',
    currentValue: 'ask',
    locked: false,
  },
  {
    id: 'browser_save',
    label: '브라우저 탭 저장',
    description: '현재 탭 본문을 Archive에 저장하는 명령',
    currentValue: 'ask',
    locked: false,
  },
  {
    id: 'browser_collect',
    label: '브라우저 자료 수집',
    description: '브라우저 자료 수집 명령',
    currentValue: 'ask',
    locked: false,
  },
  {
    id: 'file_search',
    label: '파일 검색',
    description: '로컬 파일 및 문서 검색',
    currentValue: 'allow',
    locked: false,
  },
  {
    id: 'summarize',
    label: '내용 요약',
    description: '문서 또는 페이지 요약',
    currentValue: 'allow',
    locked: false,
  },
]

// ─── 색상 ───────────────────────────────────────────────────────

const POLICY_COLORS: Record<string, { label: string; color: string; bg: string }> = {
  allow: { label: 'ALLOW', color: '#86efac', bg: '#16653420' },
  deny:  { label: 'DENY',  color: '#ffb4ab', bg: '#93000a20' },
  ask:   { label: 'ASK',   color: '#ffb786', bg: '#50240020' },
}

// ─── 컴포넌트 ───────────────────────────────────────────────────

export function PolicySettingsPanel() {
  const [rules, setRules] = useState<PolicyRule[]>(DEFAULT_RULES)
  const [saved, setSaved] = useState(false)

  function cyclePolicy(id: string) {
    setRules((prev) =>
      prev.map((rule) => {
        if (rule.id !== id || rule.locked) return rule
        const cycle: PolicyRule['currentValue'][] = ['allow', 'ask', 'deny']
        const nextIdx = (cycle.indexOf(rule.currentValue) + 1) % cycle.length
        return { ...rule, currentValue: cycle[nextIdx] }
      })
    )
    setSaved(false)
  }

  function handleSave() {
    // V1: 로컬 상태 저장 (백엔드 API 연동은 V2 확장)
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div
      className="min-h-screen flex flex-col"
      style={{ background: '#13131b', color: '#e4e1ed', fontFamily: 'Manrope, -apple-system, sans-serif' }}
    >
      {/* 헤더 */}
      <header
        className="flex items-center gap-3 px-6 py-4 border-b"
        style={{ borderColor: '#464554' }}
      >
        <span style={{ fontSize: 20 }}>⚙️</span>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, fontFamily: 'SF Pro Display, -apple-system' }}>
            Policy Settings
          </h1>
          <p style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
            Guard 정책 설정 — allow / deny / ask 기준
          </p>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-2xl mx-auto w-full">

        {/* 안내 배너 */}
        <div
          className="mb-6 p-4"
          style={{ background: '#1f1f27', borderRadius: 12, fontSize: 13, color: '#c7c4d7' }}
        >
          <span style={{ color: '#ffb786', fontWeight: 600 }}>⚠️ V1 안전 원칙</span>
          <span style={{ marginLeft: 8 }}>
            파일 삭제 · 외부 전송 · 고위험 작업은 잠금 상태입니다.
            잠금 해제는 현인님 승인 후 V2에서 지원됩니다.
          </span>
        </div>

        {/* 정책 목록 */}
        <div className="flex flex-col gap-3 mb-8">
          {rules.map((rule) => {
            const policy = POLICY_COLORS[rule.currentValue]
            return (
              <div
                key={rule.id}
                style={{
                  background: '#1f1f27',
                  borderRadius: 12,
                  padding: '16px 20px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: 16,
                }}
              >
                {/* 정책 배지 */}
                <button
                  onClick={() => cyclePolicy(rule.id)}
                  disabled={rule.locked}
                  style={{
                    background: policy.bg,
                    color: policy.color,
                    border: 'none',
                    borderRadius: 8,
                    padding: '4px 12px',
                    fontSize: 11,
                    fontWeight: 700,
                    cursor: rule.locked ? 'not-allowed' : 'pointer',
                    opacity: rule.locked ? 0.7 : 1,
                    minWidth: 60,
                    textAlign: 'center',
                    transition: '0.15s',
                    letterSpacing: '0.05em',
                  }}
                  title={rule.locked ? '잠금 — V1 기본값' : '클릭하여 순환 (allow → ask → deny)'}
                >
                  {policy.label}
                  {rule.locked && ' 🔒'}
                </button>

                {/* 규칙 설명 */}
                <div className="flex-1">
                  <div style={{ fontSize: 14, fontWeight: 600, marginBottom: 2 }}>{rule.label}</div>
                  <div style={{ fontSize: 12, color: '#888' }}>{rule.description}</div>
                </div>
              </div>
            )
          })}
        </div>

        {/* 저장 버튼 */}
        <div className="flex justify-end gap-3">
          <button
            onClick={() => setRules(DEFAULT_RULES)}
            style={{
              background: 'transparent',
              border: '1px solid #464554',
              borderRadius: 8,
              padding: '8px 20px',
              color: '#888',
              fontSize: 13,
              cursor: 'pointer',
            }}
          >
            기본값 복원
          </button>
          <button
            onClick={handleSave}
            style={{
              background: saved ? '#16653440' : '#5e5ce6',
              color: saved ? '#86efac' : '#fff',
              border: 'none',
              borderRadius: 8,
              padding: '8px 24px',
              fontSize: 13,
              fontWeight: 600,
              cursor: 'pointer',
              transition: '0.15s',
            }}
          >
            {saved ? '✓ 저장됨' : '설정 저장'}
          </button>
        </div>

        {/* 정책 설명 표 */}
        <div className="mt-10">
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#555', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
            정책 값 설명
          </h2>
          <div className="flex flex-col gap-2">
            {Object.entries(POLICY_COLORS).map(([key, val]) => (
              <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 12, fontSize: 13 }}>
                <span style={{ background: val.bg, color: val.color, padding: '2px 10px', borderRadius: 6, fontSize: 11, fontWeight: 700, minWidth: 52, textAlign: 'center' }}>
                  {val.label}
                </span>
                <span style={{ color: '#888' }}>
                  {key === 'allow' && '승인 없이 즉시 실행'}
                  {key === 'ask' && '사용자 확인 후 실행 (Action Preview 표시)'}
                  {key === 'deny' && '실행 차단 — 이유와 함께 거부'}
                </span>
              </div>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
