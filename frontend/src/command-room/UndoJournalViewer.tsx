/**
 * UndoJournalViewer — WO-006
 * 되돌릴 수 있는 작업 목록, 전/후 상태, 복구 가능 여부 표시 UI.
 * Phase 2: 표시 전용 — undo 실행은 Phase 3에서 구현합니다.
 *
 * 흐름: GET /api/v1/undo/recent → UndoEntry 목록 → 목록 + 상세 렌더링
 */
import { useEffect, useState, useCallback } from 'react'

const API_BASE = '/api/v1/undo'

// ─── 타입 정의 ──────────────────────────────────────────────────

interface UndoEntry {
  undo_id: string
  action_id: string
  operation_type: string
  before_state: string   // JSON string (from sqlite)
  after_state: string | null
  undo_available: number  // 0 or 1
  undo_method: string
  created_at: string
  completed_at: string | null
}

// ─── 헬퍼 ───────────────────────────────────────────────────────

const OPERATION_ICONS: Record<string, string> = {
  file_move: 'drive_file_move',
  file_rename: 'edit_document',
  archive_save: 'archive',
  browser_collection: 'language',
}

const OPERATION_LABELS: Record<string, string> = {
  file_move: '파일 이동',
  file_rename: '파일 이름 변경',
  archive_save: '아카이브 저장',
  browser_collection: '브라우저 수집',
}

function formatDateTime(isoString: string): string {
  const d = new Date(isoString)
  return d.toLocaleString('ko-KR', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
  })
}

function safeParseJson(s: string | null): Record<string, unknown> | null {
  if (!s) return null
  try { return JSON.parse(s) } catch { return null }
}

function JsonStateCard({ label, data }: { label: string; data: Record<string, unknown> | null }) {
  if (!data) return (
    <div className="rounded-lg bg-[#252528] p-3">
      <p className="text-[10px] text-[#555] mb-1">{label}</p>
      <p className="text-xs text-[#555] italic">없음</p>
    </div>
  )
  return (
    <div className="rounded-lg bg-[#252528] p-3">
      <p className="text-[10px] text-[#555] uppercase tracking-widest mb-2">{label}</p>
      {Object.entries(data).map(([k, v]) => (
        <div key={k} className="flex items-start gap-2 py-0.5">
          <span className="text-[10px] text-[#888] font-mono shrink-0">{k}:</span>
          <span className="text-[10px] text-[#c7c4d7] font-mono break-all">
            {String(v)}
          </span>
        </div>
      ))}
    </div>
  )
}

// ─── 컴포넌트 ──────────────────────────────────────────────────

export function UndoJournalViewer() {
  const [entries, setEntries] = useState<UndoEntry[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selected, setSelected] = useState<UndoEntry | null>(null)

  const fetchEntries = useCallback(() => {
    setLoading(true)
    fetch(`${API_BASE}/recent?limit=50`)
      .then(r => r.json())
      .then(d => {
        setEntries(d.entries ?? [])
        setLoading(false)
      })
      .catch(() => {
        setError('Undo 기록 로드 실패')
        setLoading(false)
      })
  }, [])

  useEffect(() => { fetchEntries() }, [fetchEntries])

  return (
    <div className="flex h-full bg-[#13131b] text-[#e4e1ed]">
      {/* 목록 패널 */}
      <div className="flex flex-col w-1/2 border-r border-[#252528]">
        <div className="flex items-center justify-between px-5 py-4 bg-[#1c1c1e]">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-[#c2c1ff]">settings_backup_restore</span>
            <h2 className="text-sm font-semibold">Undo Journal</h2>
          </div>
          <button
            onClick={fetchEntries}
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

        <div className="flex-1 overflow-y-auto">
          {loading && (
            <div className="flex justify-center py-8">
              <span className="material-symbols-outlined animate-spin text-[#5e5ce6]">
                progress_activity
              </span>
            </div>
          )}
          {!loading && entries.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <span className="material-symbols-outlined text-4xl text-[#464554]">
                settings_backup_restore
              </span>
              <p className="text-xs text-[#888]">되돌릴 수 있는 작업이 없습니다.</p>
            </div>
          )}
          {!loading && entries.map(entry => (
            <button
              key={entry.undo_id}
              onClick={() => setSelected(entry)}
              className={`w-full text-left px-4 py-3 border-b border-[#1c1c1e] transition-colors
                          ${selected?.undo_id === entry.undo_id ? 'bg-[#252528]' : 'hover:bg-[#1c1c1e]'}`}
            >
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-lg text-[#c7c4d7]">
                  {OPERATION_ICONS[entry.operation_type] ?? 'manage_history'}
                </span>
                <div className="flex-1 min-w-0">
                  <p className="text-xs font-medium text-[#e4e1ed]">
                    {OPERATION_LABELS[entry.operation_type] ?? entry.operation_type}
                  </p>
                  <p className="text-[10px] text-[#555] mt-0.5">
                    {formatDateTime(entry.created_at)}
                  </p>
                </div>
                {entry.undo_available ? (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#166534]/30 text-[#86efac]">
                    복구 가능
                  </span>
                ) : (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#252528] text-[#555]">
                    복구 불가
                  </span>
                )}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* 상세 패널 */}
      <div className="flex-1 flex flex-col">
        {!selected ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3">
            <span className="material-symbols-outlined text-4xl text-[#464554]">touch_app</span>
            <p className="text-xs text-[#888]">작업을 선택하면 전/후 상태가 표시됩니다.</p>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            {/* 작업 유형 */}
            <div className="flex items-center gap-3">
              <span className="material-symbols-outlined text-xl text-[#c2c1ff]">
                {OPERATION_ICONS[selected.operation_type] ?? 'manage_history'}
              </span>
              <div>
                <p className="text-sm font-semibold">
                  {OPERATION_LABELS[selected.operation_type] ?? selected.operation_type}
                </p>
                <p className="text-[10px] text-[#888]">{formatDateTime(selected.created_at)}</p>
              </div>
            </div>

            {/* 복구 가능 여부 */}
            {selected.undo_available ? (
              <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-[#166534]/20">
                <span className="material-symbols-outlined text-[#86efac] text-lg mt-0.5">
                  check_circle
                </span>
                <div>
                  <p className="text-xs font-medium text-[#86efac]">복구 가능</p>
                  <p className="text-xs text-[#c7c4d7] mt-1">{selected.undo_method}</p>
                </div>
              </div>
            ) : (
              <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-[#252528]">
                <span className="material-symbols-outlined text-[#555] text-lg">block</span>
                <p className="text-xs text-[#555]">
                  이 작업은 복구할 수 없거나 아직 완료되지 않았습니다.
                </p>
              </div>
            )}

            {/* 이전/이후 상태 */}
            <JsonStateCard label="이전 상태 (Before)" data={safeParseJson(selected.before_state)} />
            <JsonStateCard label="이후 상태 (After)" data={safeParseJson(selected.after_state)} />

            {/* Phase 3 안내 */}
            <div className="px-4 py-3 rounded-xl bg-[#1c1c1e] flex items-center gap-2">
              <span className="material-symbols-outlined text-[#888] text-sm">info</span>
              <p className="text-[10px] text-[#555]">
                Undo 실행 기능은 Phase 3에서 활성화됩니다.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
