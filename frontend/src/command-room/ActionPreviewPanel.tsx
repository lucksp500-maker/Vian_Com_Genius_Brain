/**
 * ActionPreviewPanel — WO-003
 * Web App 풀 화면 Action Preview UI.
 * action_id로 ActionSpec + preview data 조회 후 렌더링.
 *
 * 흐름: Extension HUD → chrome.tabs.create(/command-room/preview/:actionId)
 *        → 이 컴포넌트 → GET /api/v1/action-spec/:actionId → 승인/취소
 */
import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

const API_BASE = '/api/v1/action-spec'

// ─── 타입 정의 ──────────────────────────────────────────────

interface RiskDisplay {
  label: string
  color: 'success' | 'info' | 'warning' | 'error'
  icon: string
}

interface ExecutionStep {
  step: number
  label: string
  status: 'completed' | 'pending' | 'running'
  description: string
}

interface SafetyWarning {
  level: 'critical' | 'warning' | 'info'
  icon: string
  title: string
  detail: string
}

interface ActionPreviewData {
  action_id: string
  intent: string
  raw_input: string
  target_display: string
  target_ref: string | null
  risk_display: RiskDisplay
  requires_approval: boolean
  guard_result: string
  guard_reason: string | null
  execution_state: string
  execution_steps: ExecutionStep[]
  safety_warnings: SafetyWarning[]
}

interface ActionSpec {
  action_id: string
  raw_input: string
  risk_level: string
  requires_approval: boolean
  execution_state: string
}

// ─── 색상 유틸 ───────────────────────────────────────────────

const RISK_COLORS: Record<string, string> = {
  success: 'text-green-400 bg-green-400/10',
  info: 'text-blue-400 bg-blue-400/10',
  warning: 'text-[#ffb786] bg-[#ffb786]/10',
  error: 'text-[#ffb4ab] bg-[#ffb4ab]/10',
}

const STEP_ICON: Record<string, string> = {
  completed: 'check_circle',
  running: 'radio_button_checked',
  pending: 'radio_button_unchecked',
}

const STEP_COLOR: Record<string, string> = {
  completed: 'text-green-400',
  running: 'text-[#5e5ce6]',
  pending: 'text-[#464554]',
}

// ─── 컴포넌트 ────────────────────────────────────────────────

export function ActionPreviewPanel() {
  const { actionId } = useParams<{ actionId: string }>()

  const [preview, setPreview] = useState<ActionPreviewData | null>(null)
  const [spec, setSpec] = useState<ActionSpec | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [executing, setExecuting] = useState(false)
  const [result, setResult] = useState<'approved' | 'rejected' | null>(null)

  useEffect(() => {
    if (!actionId) return

    fetch(`${API_BASE}/${actionId}`)
      .then((r) => {
        if (!r.ok) throw new Error(`ActionSpec not found (${r.status})`)
        return r.json()
      })
      .then((data) => {
        setSpec(data.spec)
        setPreview(data.preview)
        setLoading(false)
      })
      .catch((e: Error) => {
        setError(e.message)
        setLoading(false)
      })
  }, [actionId])

  async function handleApprove() {
    if (!actionId) return
    setExecuting(true)
    try {
      const r = await fetch(`${API_BASE}/${actionId}/execute`, { method: 'POST' })
      if (!r.ok) throw new Error(`Execute failed (${r.status})`)
      setResult('approved')
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setExecuting(false)
    }
  }

  async function handleDecline() {
    if (!actionId) return
    await fetch(`${API_BASE}/${actionId}/reject`, { method: 'POST' })
    setResult('rejected')
  }

  // ─── 로딩 / 오류 상태 ─────────────────────────────────────

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#13131b]">
        <div className="flex flex-col items-center gap-4">
          <span className="material-symbols-outlined text-[#5e5ce6] text-4xl animate-spin">
            autorenew
          </span>
          <p className="text-[#c7c4d7] font-mono text-sm">Action Preview 로딩 중...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#13131b]">
        <div className="bg-[#1c1c1e] rounded-xl p-8 max-w-md text-center">
          <span className="material-symbols-outlined text-[#ffb4ab] text-4xl block mb-4">
            error
          </span>
          <p className="text-[#e4e1ed] font-semibold mb-2">오류 발생</p>
          <p className="text-[#c7c4d7] text-sm">{error}</p>
        </div>
      </div>
    )
  }

  if (result === 'approved') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#13131b]">
        <div className="bg-[#1c1c1e] rounded-xl p-8 max-w-md text-center">
          <span className="material-symbols-outlined text-green-400 text-5xl block mb-4">
            check_circle
          </span>
          <p className="text-[#e4e1ed] font-semibold text-xl mb-2">작업 승인됨</p>
          <p className="text-[#888] text-sm">실행 커널 연결 후 처리됩니다 (WO-011+).</p>
        </div>
      </div>
    )
  }

  if (result === 'rejected') {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#13131b]">
        <div className="bg-[#1c1c1e] rounded-xl p-8 max-w-md text-center">
          <span className="material-symbols-outlined text-[#c7c4d7] text-5xl block mb-4">
            cancel
          </span>
          <p className="text-[#e4e1ed] font-semibold text-xl mb-2">작업 취소됨</p>
          <p className="text-[#888] text-sm">이 작업은 실행되지 않았습니다.</p>
        </div>
      </div>
    )
  }

  if (!preview || !spec) return null

  const riskColor = RISK_COLORS[preview.risk_display.color] ?? RISK_COLORS.info

  // ─── 메인 렌더 ─────────────────────────────────────────────

  return (
    <div className="min-h-screen bg-[#13131b] font-sans">

      {/* 상단 헤더 */}
      <header className="fixed top-0 w-full z-50 flex justify-between items-center px-6 h-14 bg-[#1c1c1e]">
        <span className="text-white font-black tracking-widest text-sm uppercase">
          Vian CommandOS
        </span>
        <span className="text-[#5e5ce6] font-mono text-xs uppercase tracking-widest">
          Action Preview
        </span>
      </header>

      {/* 본문 (배경 딤 처리) */}
      <main className="pt-14 flex items-start justify-center min-h-[calc(100vh-3.5rem)] bg-black/60 backdrop-blur-sm p-6">

        <div className="w-full max-w-4xl bg-[#1c1c1e] rounded-xl overflow-hidden">

          {/* HUD 상단 강조선 */}
          <div className="h-0.5 w-full bg-gradient-to-r from-transparent via-[#5e5ce6] to-transparent opacity-60" />

          <div className="p-8">

            {/* 헤더: 상태 뱃지 + 제목 + 위험도 */}
            <div className="flex justify-between items-start mb-8">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="bg-[#5e5ce6]/20 text-[#5e5ce6] px-2 py-0.5 rounded text-[10px] font-mono uppercase tracking-widest">
                    Pending Review
                  </span>
                  <span className="text-[#464554] font-mono text-[10px]">
                    ID: {spec.action_id.slice(0, 8).toUpperCase()}
                  </span>
                </div>
                <h1 className="font-display text-2xl font-semibold text-white mb-1">
                  Action Plan Review
                </h1>
                <p className="text-[#c7c4d7] text-sm max-w-lg">
                  {preview.intent}
                </p>
              </div>

              <div className={`flex items-center gap-2 px-4 py-2 rounded-lg ${riskColor}`}>
                <span className="material-symbols-outlined text-base">
                  {preview.risk_display.icon}
                </span>
                <span className="font-mono text-xs uppercase font-bold tracking-widest">
                  {preview.risk_display.label}
                </span>
              </div>
            </div>

            {/* 12-column 그리드 */}
            <div className="grid grid-cols-12 gap-6">

              {/* 왼쪽: 입력 정보 + Execution Breakdown (8 cols) */}
              <div className="col-span-12 lg:col-span-8 space-y-4">

                {/* 원본 명령 */}
                <div className="bg-[#1f1f27] rounded-lg p-4">
                  <p className="text-[#464554] font-mono text-[10px] uppercase tracking-widest mb-2">
                    원본 명령
                  </p>
                  <p className="text-[#e4e1ed] font-mono text-sm">
                    "{preview.raw_input}"
                  </p>
                </div>

                {/* 대상 정보 */}
                <div className="bg-[#1f1f27] rounded-lg p-4">
                  <p className="text-[#464554] font-mono text-[10px] uppercase tracking-widest mb-2">
                    대상
                  </p>
                  <div className="flex items-center gap-2">
                    <span className="text-[#c7c4d7] text-sm">{preview.target_display}</span>
                    {preview.target_ref && (
                      <span className="text-[#5e5ce6] font-mono text-xs">
                        — {preview.target_ref}
                      </span>
                    )}
                  </div>
                </div>

                {/* Guard 판정 결과 */}
                <div className="bg-[#1f1f27] rounded-lg p-4">
                  <p className="text-[#464554] font-mono text-[10px] uppercase tracking-widest mb-2">
                    Guard 판정
                  </p>
                  <div className="flex items-center gap-2">
                    <span className={`font-mono text-xs uppercase font-bold px-2 py-0.5 rounded ${
                      preview.guard_result === 'allow'
                        ? 'bg-green-400/10 text-green-400'
                        : preview.guard_result === 'deny'
                        ? 'bg-[#ffb4ab]/10 text-[#ffb4ab]'
                        : 'bg-[#ffb786]/10 text-[#ffb786]'
                    }`}>
                      {preview.guard_result?.toUpperCase()}
                    </span>
                    {preview.guard_reason && (
                      <span className="text-[#888] text-xs">{preview.guard_reason}</span>
                    )}
                  </div>
                </div>

                {/* Execution Breakdown */}
                <div className="bg-[#1f1f27] rounded-lg p-4">
                  <p className="text-[#464554] font-mono text-[10px] uppercase tracking-widest mb-4">
                    Execution Breakdown
                  </p>
                  <div className="space-y-3">
                    {preview.execution_steps.map((step) => (
                      <div key={step.step} className="flex items-start gap-3">
                        <span className={`material-symbols-outlined text-base mt-0.5 ${STEP_COLOR[step.status]}`}>
                          {STEP_ICON[step.status]}
                        </span>
                        <div>
                          <p className="text-[#e4e1ed] text-sm font-medium">{step.label}</p>
                          <p className="text-[#888] text-xs mt-0.5">{step.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* 오른쪽: System Context + Safety Warnings (4 cols) */}
              <div className="col-span-12 lg:col-span-4 space-y-4">

                {/* System Context */}
                <div className="bg-[#1f1f27] rounded-lg p-4">
                  <p className="text-[#464554] font-mono text-[10px] uppercase tracking-widest mb-3">
                    System Context
                  </p>
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs">
                      <span className="text-[#888]">위험도</span>
                      <span className="text-[#e4e1ed] font-mono">{spec.risk_level}</span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-[#888]">승인 필요</span>
                      <span className={`font-mono ${spec.requires_approval ? 'text-[#ffb786]' : 'text-green-400'}`}>
                        {spec.requires_approval ? 'YES' : 'NO'}
                      </span>
                    </div>
                    <div className="flex justify-between text-xs">
                      <span className="text-[#888]">상태</span>
                      <span className="text-[#c2c1ff] font-mono uppercase">{spec.execution_state}</span>
                    </div>
                  </div>
                </div>

                {/* Safety Warnings */}
                {preview.safety_warnings.length > 0 && (
                  <div className="bg-[#1f1f27] rounded-lg p-4">
                    <p className="text-[#464554] font-mono text-[10px] uppercase tracking-widest mb-3">
                      Safety Warnings
                    </p>
                    <div className="space-y-3">
                      {preview.safety_warnings.map((w, i) => (
                        <div key={i} className="flex items-start gap-2">
                          <span className={`material-symbols-outlined text-sm mt-0.5 ${
                            w.level === 'critical' ? 'text-[#ffb4ab]' : 'text-[#ffb786]'
                          }`}>
                            {w.icon}
                          </span>
                          <div>
                            <p className="text-[#e4e1ed] text-xs font-semibold">{w.title}</p>
                            <p className="text-[#888] text-[11px] mt-0.5">{w.detail}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>

            {/* 하단 버튼 */}
            <div className="flex gap-3 mt-8">
              <button
                onClick={handleApprove}
                disabled={executing || preview.guard_result === 'deny'}
                className="flex-1 py-3 bg-[#5e5ce6] hover:bg-[#4d4ad5] disabled:opacity-40
                           text-white font-mono text-xs uppercase tracking-widest rounded-lg
                           transition-colors duration-150 flex items-center justify-center gap-2"
              >
                {executing ? (
                  <span className="material-symbols-outlined text-base animate-spin">autorenew</span>
                ) : (
                  <span className="material-symbols-outlined text-base">check</span>
                )}
                Approve and Execute
              </button>

              <button
                onClick={handleDecline}
                disabled={executing}
                className="flex-1 py-3 bg-[#2a2932] hover:bg-[#34343d] disabled:opacity-40
                           text-[#c7c4d7] font-mono text-xs uppercase tracking-widest rounded-lg
                           transition-colors duration-150 flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined text-base">close</span>
                Decline and Terminate
              </button>
            </div>

          </div>
        </div>
      </main>
    </div>
  )
}
