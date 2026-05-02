/**
 * CommandHUD — WO-003
 * Chrome Extension 팝업 HUD. 400px 컴팩트 레이아웃.
 *
 * 흐름:
 * 1. Ctrl+K / Cmd+K → HUD 팝업
 * 2. 자연어 입력 → callCreate() → ActionSpec 1차 결과
 * 3. riskLevel > none → chrome.tabs.create(previewUrl)
 * 4. riskLevel = none, guardResult = allow → 즉시 결과 표시
 *
 * [의존성] 연결: useCommandIntent.callCreate / 단독 수정 금지
 */
import React, { useReducer, useRef, KeyboardEvent } from 'react'
import { callCreate, shouldOpenPreviewTab, CommandIntentResult } from './useCommandIntent'

// ─── 상태 관리 ─────────────────────────────────────────────

type HudState =
  | { phase: 'idle' }
  | { phase: 'loading' }
  | { phase: 'result'; result: CommandIntentResult }
  | { phase: 'error'; message: string }
  | { phase: 'opening_preview' }

type HudAction =
  | { type: 'SUBMIT' }
  | { type: 'SUCCESS'; result: CommandIntentResult }
  | { type: 'ERROR'; message: string }
  | { type: 'RESET' }
  | { type: 'OPENING_PREVIEW' }

function reducer(state: HudState, action: HudAction): HudState {
  switch (action.type) {
    case 'SUBMIT': return { phase: 'loading' }
    case 'SUCCESS': return { phase: 'result', result: action.result }
    case 'ERROR': return { phase: 'error', message: action.message }
    case 'RESET': return { phase: 'idle' }
    case 'OPENING_PREVIEW': return { phase: 'opening_preview' }
    default: return state
  }
}

// ─── 색상 유틸 ─────────────────────────────────────────────

const RISK_BADGE: Record<string, { label: string; cls: string }> = {
  none: { label: '안전', cls: 'bg-green-400/10 text-green-400' },
  low: { label: '낮음', cls: 'bg-blue-400/10 text-blue-300' },
  medium: { label: '중간', cls: 'bg-[#ffb786]/10 text-[#ffb786]' },
  high: { label: '높음', cls: 'bg-[#ffb4ab]/10 text-[#ffb4ab]' },
}

const GUARD_BADGE: Record<string, { label: string; cls: string }> = {
  allow: { label: 'ALLOW', cls: 'text-green-400' },
  ask: { label: 'ASK', cls: 'text-[#ffb786]' },
  deny: { label: 'DENY', cls: 'text-[#ffb4ab]' },
}

// ─── 컴포넌트 ──────────────────────────────────────────────

export function CommandHUD() {
  const [state, dispatch] = useReducer(reducer, { phase: 'idle' })
  const [input, setInput] = React.useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  async function handleSubmit() {
    const trimmed = input.trim()
    if (!trimmed || state.phase === 'loading') return

    dispatch({ type: 'SUBMIT' })

    try {
      const result = await callCreate(trimmed)

      if (shouldOpenPreviewTab(result) && result.previewUrl) {
        dispatch({ type: 'OPENING_PREVIEW' })
        // Chrome Extension API: 새 탭으로 Preview 열기
        if (typeof chrome !== 'undefined' && chrome.tabs) {
          await chrome.tabs.create({ url: result.previewUrl, active: true })
        } else {
          // 개발 환경 fallback
          window.open(result.previewUrl, '_blank')
        }
        setTimeout(() => window.close(), 500)
      } else {
        dispatch({ type: 'SUCCESS', result })
      }
    } catch (e: unknown) {
      dispatch({
        type: 'ERROR',
        message: e instanceof Error ? e.message : '알 수 없는 오류',
      })
    }
  }

  function handleKeyDown(e: KeyboardEvent<HTMLInputElement>) {
    if (e.key === 'Enter') handleSubmit()
    if (e.key === 'Escape') dispatch({ type: 'RESET' })
  }

  // ─── 렌더 ────────────────────────────────────────────────

  return (
    <div
      style={{ width: 400, minHeight: 120 }}
      className="bg-[#1c1c1e] font-sans text-[#e4e1ed] select-none"
    >
      {/* HUD 상단 강조선 */}
      <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-[#5e5ce6] to-transparent opacity-60" />

      <div className="p-4">
        {/* 타이틀 */}
        <div className="flex items-center justify-between mb-3">
          <span className="font-mono text-[10px] uppercase tracking-widest text-[#5e5ce6]">
            Vian CommandOS
          </span>
          <span className="font-mono text-[10px] text-[#464554]">
            HUD v2.0
          </span>
        </div>

        {/* 입력 필드 */}
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#464554] text-base">
            psychology
          </span>
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="자연어로 명령하세요..."
            disabled={state.phase === 'loading' || state.phase === 'opening_preview'}
            autoFocus
            className="w-full bg-[#13131b] text-[#e4e1ed] placeholder-[#464554]
                       font-sans text-sm pl-10 pr-4 py-2.5 rounded-lg outline-none
                       focus:bg-[#2a2932] transition-colors duration-150
                       disabled:opacity-50"
          />
        </div>

        {/* 상태별 결과 표시 */}
        {state.phase === 'loading' && (
          <div className="mt-3 flex items-center gap-2 text-[#c7c4d7] text-xs">
            <span className="material-symbols-outlined text-sm text-[#5e5ce6] animate-spin">
              autorenew
            </span>
            AI 분석 중...
          </div>
        )}

        {state.phase === 'opening_preview' && (
          <div className="mt-3 flex items-center gap-2 text-[#c7c4d7] text-xs">
            <span className="material-symbols-outlined text-sm text-[#5e5ce6]">
              open_in_new
            </span>
            Preview 탭 열리는 중...
          </div>
        )}

        {state.phase === 'result' && (() => {
          const r = state.result
          const risk = RISK_BADGE[r.riskLevel] ?? RISK_BADGE.medium
          const guard = GUARD_BADGE[r.guardResult] ?? GUARD_BADGE.ask
          return (
            <div className="mt-3 bg-[#13131b] rounded-lg p-3 space-y-2">
              <p className="text-[#e4e1ed] text-xs">{r.intent}</p>
              <div className="flex items-center gap-2">
                <span className={`px-1.5 py-0.5 rounded text-[10px] font-mono uppercase ${risk.cls}`}>
                  {risk.label}
                </span>
                <span className={`font-mono text-[10px] uppercase ${guard.cls}`}>
                  {guard.label}
                </span>
              </div>
              <button
                onClick={() => { dispatch({ type: 'RESET' }); setInput('') }}
                className="text-[#464554] font-mono text-[10px] hover:text-[#c7c4d7] transition-colors"
              >
                ← 새 명령
              </button>
            </div>
          )
        })()}

        {state.phase === 'error' && (
          <div className="mt-3 bg-[#ffb4ab]/10 rounded-lg p-3">
            <p className="text-[#ffb4ab] text-xs">{state.message}</p>
            <button
              onClick={() => dispatch({ type: 'RESET' })}
              className="text-[#464554] font-mono text-[10px] hover:text-[#c7c4d7] mt-1 transition-colors"
            >
              ← 다시 시도
            </button>
          </div>
        )}

        {/* 단축키 안내 */}
        {state.phase === 'idle' && (
          <div className="mt-3 flex items-center gap-3">
            <span className="text-[#464554] font-mono text-[10px]">Enter 실행</span>
            <span className="text-[#464554] font-mono text-[10px]">Esc 닫기</span>
          </div>
        )}
      </div>
    </div>
  )
}
