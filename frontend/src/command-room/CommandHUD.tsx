/**
 * CommandHUD — WO-008
 * Command Room 진입점 HUD (웹 앱 전체 화면 버전).
 * Extension HUD(400px 팝업)와 다릅니다 — 이것은 /command-room 의 메인 랜딩 UI입니다.
 *
 * 흐름:
 *   1. 자연어 입력 → POST /api/v1/intent/create → ActionSpec
 *   2. Guard 결과 표시
 *   3. risk > none 또는 requires_approval → ActionPreviewPanel 이동
 *   4. risk = none → 즉시 결과 표시
 *   5. 브라우저 명령 (저장/요약/수집) → BrowserCollectionRoom 이동
 *
 * [의존성] 연결: /api/v1/intent/create / 단독 수정 금지
 */
import { useReducer, useRef, useEffect, KeyboardEvent } from 'react'
import { useNavigate } from 'react-router-dom'

const API_BASE = '/api/v1/intent'

// ─── 타입 ───────────────────────────────────────────────────────

interface IntentResult {
  action_id: string
  intent: string
  target_type: string
  risk_level: string
  requires_approval: boolean
  guard_result: string | null
  guard_reason: string | null
  execution_state: string
  confidence_score: number | null
  preview_url: string | null
}

type Phase =
  | { name: 'idle' }
  | { name: 'loading' }
  | { name: 'result'; data: IntentResult }
  | { name: 'error'; message: string }
  | { name: 'redirecting' }

type Action =
  | { type: 'SUBMIT' }
  | { type: 'SUCCESS'; data: IntentResult }
  | { type: 'ERROR'; message: string }
  | { type: 'RESET' }
  | { type: 'REDIRECTING' }

function reducer(state: Phase, action: Action): Phase {
  switch (action.type) {
    case 'SUBMIT': return { name: 'loading' }
    case 'SUCCESS': return { name: 'result', data: action.data }
    case 'ERROR': return { name: 'error', message: action.message }
    case 'RESET': return { name: 'idle' }
    case 'REDIRECTING': return { name: 'redirecting' }
    default: return state
  }
}

// ─── 추천 명령어 ─────────────────────────────────────────────────

const SUGGESTIONS = [
  '어제 받은 견적서 찾아줘',
  '이 PDF 요약해줘',
  '현재 탭 저장해줘',
  '최근 다운로드 파일 보여줘',
]

const BROWSER_KEYWORDS = ['탭 저장', '페이지 요약', '자료 수집', 'save_tab', 'summarize', 'collect']

function isBrowserCommand(input: string): boolean {
  return BROWSER_KEYWORDS.some((kw) => input.toLowerCase().includes(kw.toLowerCase()))
}

// ─── 컴포넌트 ───────────────────────────────────────────────────

export function CommandHUD() {
  const [state, dispatch] = useReducer(reducer, { name: 'idle' })
  const [, setInput] = useReducer((_: string, v: string) => v, '')
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()

  useEffect(() => {
    inputRef.current?.focus()
  }, [])

  async function handleSubmit() {
    const trimmed = (inputRef.current?.value || '').trim()
    if (!trimmed || state.name === 'loading') return

    // 브라우저 명령 → BrowserCollectionRoom 이동
    if (isBrowserCommand(trimmed)) {
      navigate('/command-room/browser-collection')
      return
    }

    dispatch({ type: 'SUBMIT' })

    try {
      const res = await fetch(`${API_BASE}/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ raw_input: trimmed, source: 'hud' }),
      })
      if (!res.ok) throw new Error(`서버 오류: ${res.status}`)
      const data: IntentResult = await res.json()
      dispatch({ type: 'SUCCESS', data })

      // 승인 필요 → Action Preview로 자동 이동
      if ((data.requires_approval || data.risk_level !== 'none') && data.action_id) {
        dispatch({ type: 'REDIRECTING' })
        setTimeout(() => {
          navigate(`/command-room/preview/${data.action_id}`)
        }, 800)
      }
    } catch (err) {
      dispatch({ type: 'ERROR', message: String(err) })
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') handleSubmit()
    if (e.key === 'Escape') {
      dispatch({ type: 'RESET' })
      setInput('')
    }
  }

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-start pt-24 px-4"
      style={{ background: '#13131b', color: '#e4e1ed', fontFamily: 'Manrope, -apple-system, sans-serif' }}
    >
      {/* 로고 / 타이틀 */}
      <div className="text-center mb-12">
        <h1 style={{ fontSize: 32, fontWeight: 700, fontFamily: 'SF Pro Display, -apple-system', letterSpacing: '-0.01em', marginBottom: 8 }}>
          Vian CommandOS
        </h1>
        <p style={{ fontSize: 14, color: '#888' }}>
          자연어로 명령하세요 — 찾고, 보여주고, 승인 후 실행합니다
        </p>
      </div>

      {/* 입력창 */}
      <div
        className="w-full max-w-2xl relative"
        style={{ marginBottom: 24 }}
      >
        <div
          style={{
            background: '#1f1f27',
            borderRadius: 16,
            display: 'flex',
            alignItems: 'center',
            gap: 12,
            padding: '14px 20px',
            boxShadow: state.name === 'loading'
              ? '0 0 0 2px #5e5ce6'
              : '0 0 0 1px #464554',
            transition: '0.15s',
          }}
        >
          <span style={{ fontSize: 18, flexShrink: 0 }}>
            {state.name === 'loading' ? '⏳' : '💬'}
          </span>
          <input
            ref={inputRef}
            defaultValue=""
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="명령을 입력하세요... (Enter)"
            disabled={state.name === 'loading'}
            style={{
              flex: 1,
              background: 'transparent',
              border: 'none',
              outline: 'none',
              color: '#e4e1ed',
              fontSize: 16,
              fontFamily: 'Manrope, -apple-system, sans-serif',
            }}
          />
          <button
            onClick={handleSubmit}
            disabled={state.name === 'loading'}
            style={{
              background: '#5e5ce6',
              border: 'none',
              borderRadius: 8,
              padding: '6px 16px',
              color: '#fff',
              fontSize: 13,
              fontWeight: 600,
              cursor: state.name === 'loading' ? 'not-allowed' : 'pointer',
              opacity: state.name === 'loading' ? 0.6 : 1,
              transition: '0.15s',
              flexShrink: 0,
            }}
          >
            실행
          </button>
        </div>
      </div>

      {/* 결과 영역 */}
      {state.name === 'result' && <ResultCard data={state.data} />}
      {state.name === 'error' && <ErrorCard message={state.message} />}
      {state.name === 'redirecting' && (
        <div style={{ color: '#c2c1ff', fontSize: 14 }}>Action Preview 이동 중...</div>
      )}

      {/* 추천 명령 */}
      {state.name === 'idle' && (
        <div className="w-full max-w-2xl mt-8">
          <p style={{ fontSize: 12, color: '#555', marginBottom: 12, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
            추천 명령
          </p>
          <div className="grid gap-2" style={{ gridTemplateColumns: '1fr 1fr' }}>
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                onClick={() => {
                  if (inputRef.current) {
                    inputRef.current.value = s
                    setInput(s)
                    inputRef.current.focus()
                  }
                }}
                style={{
                  background: '#1b1b23',
                  border: 'none',
                  borderRadius: 10,
                  padding: '10px 16px',
                  color: '#c7c4d7',
                  fontSize: 13,
                  textAlign: 'left',
                  cursor: 'pointer',
                  transition: '0.15s',
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* 네비게이션 */}
      <nav className="w-full max-w-2xl mt-12 flex flex-wrap gap-3 justify-center">
        {[
          { label: '🔍 검색', path: '/command-room/local-search' },
          { label: '🌐 브라우저', path: '/command-room/browser-collection' },
          { label: '📋 Audit', path: '/command-room/audit' },
          { label: '↩️ Undo', path: '/command-room/undo' },
          { label: '⚙️ 정책', path: '/command-room/policy' },
        ].map(({ label, path }) => (
          <button
            key={path}
            onClick={() => navigate(path)}
            style={{
              background: 'transparent',
              border: '1px solid #464554',
              borderRadius: 8,
              padding: '6px 16px',
              color: '#888',
              fontSize: 12,
              cursor: 'pointer',
              transition: '0.15s',
            }}
          >
            {label}
          </button>
        ))}
      </nav>
    </div>
  )
}

// ─── 결과 카드 ──────────────────────────────────────────────────

function ResultCard({ data }: { data: IntentResult }) {
  const RISK: Record<string, { label: string; color: string; bg: string }> = {
    none: { label: '안전', color: '#86efac', bg: '#16653480' },
    low: { label: '낮음', color: '#7dd3fc', bg: '#1e3a5f80' },
    medium: { label: '중간', color: '#ffb786', bg: '#50240080' },
    high: { label: '높음', color: '#ffb4ab', bg: '#93000a80' },
  }
  const GUARD: Record<string, { label: string; color: string }> = {
    allow: { label: 'ALLOW', color: '#86efac' },
    ask: { label: 'ASK', color: '#ffb786' },
    deny: { label: 'DENY', color: '#ffb4ab' },
  }

  const risk = RISK[data.risk_level] || RISK['none']
  const guard = GUARD[data.guard_result || ''] || { label: data.guard_result || '-', color: '#888' }

  return (
    <div
      className="w-full max-w-2xl"
      style={{ background: '#1f1f27', borderRadius: 16, padding: '20px 24px' }}
    >
      <div className="flex items-center gap-3 mb-4">
        <span style={{ background: risk.bg, color: risk.color, padding: '2px 10px', borderRadius: 20, fontSize: 12 }}>
          {risk.label}
        </span>
        <span style={{ color: guard.color, fontSize: 12, fontWeight: 600 }}>{guard.label}</span>
        {data.confidence_score != null && (
          <span style={{ color: '#888', fontSize: 12 }}>
            확신도 {Math.round(data.confidence_score * 100)}%
          </span>
        )}
      </div>
      <p style={{ fontSize: 14, color: '#e4e1ed', marginBottom: 8 }}>{data.intent || '처리 완료'}</p>
      {data.guard_reason && (
        <p style={{ fontSize: 12, color: '#888' }}>{data.guard_reason}</p>
      )}
      {data.requires_approval && (
        <p style={{ fontSize: 12, color: '#c2c1ff', marginTop: 8 }}>
          Action Preview로 이동합니다...
        </p>
      )}
    </div>
  )
}

function ErrorCard({ message }: { message: string }) {
  return (
    <div
      className="w-full max-w-2xl"
      style={{ background: '#2d1515', borderRadius: 12, padding: '16px 24px', border: '1px solid #93000a' }}
    >
      <p style={{ color: '#ffb4ab', fontSize: 14 }}>⚠️ {message}</p>
    </div>
  )
}
