/**
 * AuditLedgerViewer — WO-006
 * CommandOS 명령 이력 및 판단 결과 표시 UI.
 * Guard 판정, 승인 여부, 실행 결과, 실패 원인을 타임라인 형식으로 보여줍니다.
 *
 * 흐름: GET /api/v1/audit/recent → AuditRecord 목록 → 타임라인 렌더링
 */
import { useEffect, useState, useCallback } from 'react'

const API_BASE = '/api/v1/audit'

// ─── 타입 정의 ──────────────────────────────────────────────────

interface AuditRecord {
  audit_id: string
  command: string
  action_spec_id: string
  intent_class: string
  risk_class: string
  guard_decision: string
  approval_result: string
  execution_result: string | null
  error: string | null
  confidence: number | null
  created_at: string
}

// ─── 헬퍼 ─────────────────────────────────���─────────────────────

const GUARD_COLORS: Record<string, string> = {
  allow: 'text-[#86efac]',
  deny: 'text-[#ffb4ab]',
  ask: 'text-[#ffb786]',
  pending: 'text-[#888]',
}

const EXECUTION_COLORS: Record<string, string> = {
  executed: 'text-[#86efac]',
  failed: 'text-[#ffb4ab]',
  user_rejected: 'text-[#c7c4d7]',
  stopped: 'text-[#ffb786]',
  pending: 'text-[#888]',
}

const RISK_LABELS: Record<string, { label: string; color: string }> = {
  none: { label: '안전', color: 'bg-[#166534]/30 text-[#86efac]' },
  low: { label: '낮음', color: 'bg-[#1e3a5f]/30 text-[#7dd3fc]' },
  medium: { label: '중간', color: 'bg-[#502400]/30 text-[#ffb786]' },
  high: { label: '높음', color: 'bg-[#93000a]/30 text-[#ffb4ab]' },
}

function formatDateTime(isoString: string): string {
  const d = new Date(isoString)
  return d.toLocaleString('ko-KR', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
}

function ConfidenceBadge({ score }: { score: number | null }) {
  if (score === null) return null
  const pct = Math.round(score * 100)
  const color = score >= 0.7 ? '#86efac' : score >= 0.4 ? '#ffb786' : '#ffb4ab'
  return (
    <span className="text-xs font-mono" style={{ color }}>
      {pct}%
    </span>
  )
}

// ─── 컴포넌트 ─────────────────────────────���────────────────────

export function AuditLedgerViewer() {
  const [records, setRecords] = useState<AuditRecord[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<AuditRecord | null>(null)

  const fetchRecords = useCallback(() => {
    setLoading(true)
    fetch(`${API_BASE}/recent?limit=50`)
      .then(r => r.json())
      .then(d => {
        setRecords(d.records ?? [])
        setLoading(false)
      })
      .catch(() => {
        setError('Audit 기록 로드 실패')
        setLoading(false)
      })
  }, [])

  useEffect(() => { fetchRecords() }, [fetchRecords])

  return (
    <div className="flex h-full bg-[#13131b] text-[#e4e1ed]">
      {/* 목록 패널 */}
      <div className="flex flex-col w-1/2 border-r border-[#252528]">
        {/* 헤더 */}
        <div className="flex items-center justify-between px-5 py-4 bg-[#1c1c1e]">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-[#c2c1ff]">history_edu</span>
            <h2 className="text-sm font-semibold">Audit Ledger</h2>
          </div>
          <button
            onClick={fetchRecords}
            className="p-1.5 rounded-lg hover:bg-[#252528] transition-colors text-[#888]"
          >
            <span className="material-symbols-outlined text-base">refresh</span>
          </button>
        </div>

        {error && (
          <div className="mx-4 mt-3 px-3 py-2 rounded-lg bg-[#93000a]/20 text-[#ffb4ab] text-xs">
            {error}
          </div>
        )}

        {/* 기록 목록 */}
        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="flex justify-center py-8">
              <span className="material-symbols-outlined animate-spin text-[#5e5ce6]">
                progress_activity
              </span>
            </div>
          )}
          {!loading && records.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <span className="material-symbols-outlined text-4xl text-[#464554]">receipt_long</span>
              <p className="text-xs text-[#888]">아직 명령 기록이 없습니다.</p>
            </div>
          )}
          {!loading && records.map(rec => (
            <button
              key={rec.audit_id}
              onClick={() => setSelected(rec)}
              className={`w-full text-left px-4 py-3 border-b border-[#1c1c1e] transition-colors
                          ${selected?.audit_id === rec.audit_id
                  ? 'bg-[#252528]' : 'hover:bg-[#1c1c1e]'}`}
            >
              <div className="flex items-start justify-between gap-2">
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-[#e4e1ed] truncate">{rec.command}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className={`text-[10px] font-mono ${GUARD_COLORS[rec.guard_decision] ?? 'text-[#888]'}`}>
                      {rec.guard_decision}
                    </span>
                    <span className="text-[#464554]">·</span>
                    <span className={`text-[10px] ${EXECUTION_COLORS[rec.execution_result ?? 'pending'] ?? 'text-[#888]'}`}>
                      {rec.execution_result ?? 'pending'}
                    </span>
                    {rec.confidence !== null && (
                      <>
                        <span className="text-[#464554]">·</span>
                        <ConfidenceBadge score={rec.confidence} />
                      </>
                    )}
                  </div>
                </div>
                <span className="text-[10px] text-[#555] shrink-0 mt-0.5">
                  {formatDateTime(rec.created_at)}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 상세 패널 */}
      <div className="flex-1 flex flex-col">
        {!selected ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3">
            <span className="material-symbols-outlined text-4xl text-[#464554]">
              touch_app
            </span>
            <p className="text-xs text-[#888]">명령 기록을 선택하면 상세 정보가 표시됩니다.</p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {/* 명령 */}
            <div className="rounded-xl bg-[#1c1c1e] p-4">
              <p className="text-[10px] text-[#555] uppercase tracking-widest mb-1">명령 입력</p>
              <p className="text-sm text-[#e4e1ed] font-medium">{selected.command}</p>
            </div>

            {/* 판단 결과 그리드 */}
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-[#1c1c1e] p-3">
                <p className="text-[10px] text-[#555] uppercase tracking-widest mb-1">Intent</p>
                <p className="text-xs text-[#c7c4d7]">{selected.intent_class || '—'}</p>
              </div>
              <div className="rounded-xl bg-[#1c1c1e] p-3">
                <p className="text-[10px] text-[#555] uppercase tracking-widest mb-1">Risk</p>
                <span className={`text-xs px-2 py-0.5 rounded-full ${(RISK_LABELS[selected.risk_class] ?? RISK_LABELS['none']).color}`}>
                  {(RISK_LABELS[selected.risk_class] ?? { label: selected.risk_class }).label}
                </span>
              </div>
              <div className="rounded-xl bg-[#1c1c1e] p-3">
                <p className="text-[10px] text-[#555] uppercase tracking-widest mb-1">Guard 판정</p>
                <p className={`text-xs font-mono ${GUARD_COLORS[selected.guard_decision] ?? 'text-[#888]'}`}>
                  {selected.guard_decision}
                </p>
              </div>
              <div className="rounded-xl bg-[#1c1c1e] p-3">
                <p className="text-[10px] text-[#555] uppercase tracking-widest mb-1">Confidence</p>
                <ConfidenceBadge score={selected.confidence} />
                {selected.confidence === null && <span className="text-xs text-[#555]">—</span>}
              </div>
            </div>

            {/* 실행 결과 */}
            <div className="rounded-xl bg-[#1c1c1e] p-4">
              <p className="text-[10px] text-[#555] uppercase tracking-widest mb-2">실행 결과</p>
              <p className={`text-sm font-mono ${EXECUTION_COLORS[selected.execution_result ?? 'pending'] ?? 'text-[#888]'}`}>
                {selected.execution_result ?? 'pending'}
              </p>
              {selected.error && (
                <div className="mt-3 p-3 rounded-lg bg-[#93000a]/20">
                  <p className="text-xs text-[#ffb4ab]">{selected.error}</p>
                </div>
              )}
            </div>

            {/* 시각 */}
            <p className="text-[10px] text-[#555] font-mono text-right">
              {formatDateTime(selected.created_at)}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
