/**
 * BrowserCollectionRoom — WO-007
 * 브라우저 탭 저장 / 페이지 요약 / 자료 수집 UI.
 * Extension과 연동하여 현재 탭 데이터 수집 명령을 표시하고 결과를 보여줍니다.
 *
 * 흐름:
 *   1. 사용자가 Extension HUD에서 브라우저 명령 실행
 *   2. browserCommandRouter.ts → POST /api/v1/browser/collect
 *   3. 결과를 이 페이지에서 확인 (action_id, injection_risk, guard 결과)
 *   4. requires_approval=True → ActionPreviewPanel로 이동
 *
 * 직접 호출도 가능: /command-room/browser-collection
 *
 * [의존성] 연결: backend /api/v1/browser/collect / 단독 수정 금지
 */
import { useEffect, useState, useCallback } from 'react'

const API_BASE = '/api/v1/browser'

// ─── 타입 ───────────────────────────────────────────────────────

interface CollectRequest {
  action_type: 'save_tab' | 'summarize' | 'collect'
  url: string
  title: string
  raw_content: string
  meta_description: string
  word_count: number
}

interface CollectResponse {
  action_id?: string
  blocked: boolean
  block_reason: string
  injection_risk: boolean
  intent?: string
  risk_level?: string
  requires_approval?: boolean
  preview_url?: string
}

type ActionType = 'save_tab' | 'summarize' | 'collect'

type Phase =
  | { name: 'idle' }
  | { name: 'loading'; actionType: ActionType }
  | { name: 'result'; data: CollectResponse; actionType: ActionType }
  | { name: 'error'; message: string }

// ─── 상수 ───────────────────────────────────────────────────────

const ACTION_LABELS: Record<ActionType, { label: string; icon: string; desc: string }> = {
  save_tab: {
    label: '현재 탭 저장',
    icon: '💾',
    desc: '현재 페이지 본문과 URL을 Archive에 저장합니다',
  },
  summarize: {
    label: '페이지 요약',
    icon: '📋',
    desc: '현재 페이지의 핵심 내용을 요약합니다',
  },
  collect: {
    label: '자료 수집',
    icon: '📦',
    desc: '브라우저 현재 탭의 자료를 수집합니다',
  },
}

// 데모용 payload (Extension 없는 환경에서 테스트)
const DEMO_PAYLOAD: Omit<CollectRequest, 'action_type'> = {
  url: window.location.href || 'http://localhost:5051',
  title: document.title || 'Vian CommandOS',
  raw_content: '데모 페이지 본문입니다. Extension이 연결된 환경에서는 실제 페이지 본문이 전송됩니다.',
  meta_description: '데모 설명',
  word_count: 20,
}

// ─── 컴포넌트 ───────────────────────────────────────────────────

export function BrowserCollectionRoom() {
  const [phase, setPhase] = useState<Phase>({ name: 'idle' })
  const [lastResults, setLastResults] = useState<Array<{ actionType: ActionType; data: CollectResponse }>>([])

  const runAction = useCallback(async (actionType: ActionType) => {
    setPhase({ name: 'loading', actionType })

    const body: CollectRequest = {
      action_type: actionType,
      ...DEMO_PAYLOAD,
    }

    try {
      const res = await fetch(`${API_BASE}/collect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })

      if (!res.ok) throw new Error(`서버 오류: ${res.status}`)
      const data: CollectResponse = await res.json()

      setPhase({ name: 'result', data, actionType })
      setLastResults((prev) => [{ actionType, data }, ...prev.slice(0, 4)])
    } catch (err) {
      setPhase({ name: 'error', message: String(err) })
    }
  }, [])

  // 결과 → ActionPreview 자동 이동 (requires_approval + action_id 있을 때)
  useEffect(() => {
    if (phase.name === 'result' && phase.data.requires_approval && phase.data.action_id) {
      const previewUrl = phase.data.preview_url || `/command-room/preview/${phase.data.action_id}`
      const timer = setTimeout(() => {
        window.open(previewUrl, '_blank')
      }, 1500)
      return () => clearTimeout(timer)
    }
  }, [phase])

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
        <span style={{ fontSize: 20 }}>🌐</span>
        <div>
          <h1 style={{ fontSize: 18, fontWeight: 600, fontFamily: 'SF Pro Display, -apple-system' }}>
            Browser Collection Room
          </h1>
          <p style={{ fontSize: 12, color: '#888', marginTop: 2 }}>
            브라우저 탭 저장 · 페이지 요약 · 자료 수집
          </p>
        </div>
      </header>

      <main className="flex-1 p-6 max-w-2xl mx-auto w-full">

        {/* 작업 버튼 3개 */}
        <div className="grid gap-3 mb-8" style={{ gridTemplateColumns: '1fr 1fr 1fr' }}>
          {(Object.keys(ACTION_LABELS) as ActionType[]).map((type) => {
            const info = ACTION_LABELS[type]
            const isLoading = phase.name === 'loading' && phase.actionType === type
            return (
              <button
                key={type}
                onClick={() => runAction(type)}
                disabled={phase.name === 'loading'}
                style={{
                  background: '#1f1f27',
                  border: 'none',
                  borderRadius: 12,
                  padding: '16px 12px',
                  cursor: phase.name === 'loading' ? 'not-allowed' : 'pointer',
                  opacity: phase.name === 'loading' && !isLoading ? 0.5 : 1,
                  transition: '0.15s',
                  textAlign: 'center',
                }}
              >
                <div style={{ fontSize: 24, marginBottom: 8 }}>
                  {isLoading ? '⏳' : info.icon}
                </div>
                <div style={{ fontSize: 13, fontWeight: 600, color: '#e4e1ed', marginBottom: 4 }}>
                  {info.label}
                </div>
                <div style={{ fontSize: 11, color: '#888', lineHeight: 1.4 }}>
                  {info.desc}
                </div>
              </button>
            )
          })}
        </div>

        {/* 결과 표시 */}
        {phase.name === 'result' && (
          <ResultCard data={phase.data} actionType={phase.actionType} />
        )}

        {phase.name === 'error' && (
          <div
            style={{
              background: '#93000a',
              borderRadius: 12,
              padding: '16px 20px',
              color: '#ffdad6',
              fontSize: 14,
            }}
          >
            ⚠️ {phase.message}
          </div>
        )}

        {/* 최근 이력 */}
        {lastResults.length > 0 && (
          <div className="mt-8">
            <h2 style={{ fontSize: 13, fontWeight: 600, color: '#888', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
              최근 실행 이력
            </h2>
            <div className="flex flex-col gap-2">
              {lastResults.map((r, i) => (
                <HistoryRow key={i} actionType={r.actionType} data={r.data} />
              ))}
            </div>
          </div>
        )}

        {/* Prompt Injection 안내 */}
        <div
          className="mt-8 p-4"
          style={{ background: '#1f1f27', borderRadius: 12, fontSize: 12, color: '#888' }}
        >
          <span style={{ color: '#c2c1ff', fontWeight: 600 }}>🛡 Prompt Injection Shield 활성</span>
          <span style={{ marginLeft: 8 }}>
            웹 페이지 원문에 포함된 명령 주입 패턴을 자동 감지하고 차단합니다.
          </span>
        </div>
      </main>
    </div>
  )
}

// ─── 결과 카드 ──────────────────────────────────────────────────

function ResultCard({ data, actionType }: { data: CollectResponse; actionType: ActionType }) {
  const info = ACTION_LABELS[actionType]

  if (data.blocked) {
    return (
      <div style={{ background: '#2d1515', borderRadius: 12, padding: '20px 24px', border: '1px solid #93000a' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
          <span style={{ fontSize: 18 }}>🚫</span>
          <span style={{ fontWeight: 600, color: '#ffb4ab' }}>차단됨</span>
          {data.injection_risk && (
            <span style={{ background: '#93000a', color: '#ffdad6', fontSize: 11, padding: '2px 8px', borderRadius: 20 }}>
              Prompt Injection 감지
            </span>
          )}
        </div>
        <p style={{ fontSize: 13, color: '#c7c4d7' }}>{data.block_reason}</p>
      </div>
    )
  }

  return (
    <div style={{ background: '#1f1f27', borderRadius: 12, padding: '20px 24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 16 }}>
        <span style={{ fontSize: 18 }}>{info.icon}</span>
        <span style={{ fontWeight: 600, color: '#86efac' }}>처리 완료</span>
        {data.requires_approval && (
          <span style={{ background: '#1e3a5f', color: '#7dd3fc', fontSize: 11, padding: '2px 8px', borderRadius: 20 }}>
            승인 필요 → Preview 열기
          </span>
        )}
      </div>

      <dl className="grid gap-2" style={{ fontSize: 13 }}>
        {data.intent && (
          <div style={{ display: 'flex', gap: 8 }}>
            <dt style={{ color: '#888', minWidth: 80 }}>Intent</dt>
            <dd style={{ color: '#e4e1ed' }}>{data.intent}</dd>
          </div>
        )}
        {data.risk_level && (
          <div style={{ display: 'flex', gap: 8 }}>
            <dt style={{ color: '#888', minWidth: 80 }}>위험도</dt>
            <dd>
              <RiskBadge level={data.risk_level} />
            </dd>
          </div>
        )}
        {data.action_id && (
          <div style={{ display: 'flex', gap: 8 }}>
            <dt style={{ color: '#888', minWidth: 80 }}>Action ID</dt>
            <dd style={{ color: '#c7c4d7', fontFamily: 'monospace', fontSize: 11 }}>
              {data.action_id}
            </dd>
          </div>
        )}
      </dl>
    </div>
  )
}

function HistoryRow({ actionType, data }: { actionType: ActionType; data: CollectResponse }) {
  const info = ACTION_LABELS[actionType]
  return (
    <div
      style={{
        background: '#1b1b23',
        borderRadius: 8,
        padding: '10px 16px',
        display: 'flex',
        alignItems: 'center',
        gap: 10,
        fontSize: 13,
      }}
    >
      <span>{info.icon}</span>
      <span style={{ color: '#c7c4d7', flex: 1 }}>{info.label}</span>
      {data.blocked ? (
        <span style={{ color: '#ffb4ab' }}>차단</span>
      ) : (
        <span style={{ color: '#86efac' }}>처리완료</span>
      )}
    </div>
  )
}

function RiskBadge({ level }: { level: string }) {
  const map: Record<string, { label: string; color: string; bg: string }> = {
    none: { label: '안전', color: '#86efac', bg: '#166534' },
    low: { label: '낮음', color: '#7dd3fc', bg: '#1e3a5f' },
    medium: { label: '중간', color: '#ffb786', bg: '#502400' },
    high: { label: '높음', color: '#ffb4ab', bg: '#93000a' },
  }
  const s = map[level] || map['none']
  return (
    <span style={{ background: `${s.bg}50`, color: s.color, padding: '1px 8px', borderRadius: 20, fontSize: 11 }}>
      {s.label}
    </span>
  )
}
