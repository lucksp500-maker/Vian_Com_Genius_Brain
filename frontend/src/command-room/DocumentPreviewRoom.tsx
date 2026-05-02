/**
 * DocumentPreviewRoom — WO-004
 * 로컬 파일(PDF/텍스트/코드/웹) 실행 전 미리보기 UI.
 * 실행 없이 파일 내용만 표시 — 승인 전 확인 목적.
 *
 * 흐름: LocalSearchResultViewer 클릭 → encodedPath param
 *        → GET /api/v1/local-preview?path=... → PreviewResult 렌더링
 */
import { useEffect, useState } from 'react'

const API_BASE = '/api/v1/local-preview'

// ─── 타입 정의 ──────────────────────────────────────────────────

interface PreviewResult {
  path: string
  title: string
  file_type: string
  content_preview: string
  page_count: number | null
  file_size: number
  sensitive_flags: string[]
  error: string | null
  available: boolean
}

// ─── 헬퍼 ───────────────────────────────────────────────────────

const FILE_TYPE_LABELS: Record<string, string> = {
  pdf: 'PDF 문서',
  text: '텍스트',
  code: '코드',
  web: '웹 페이지',
  unknown: '알 수 없음',
}

const FILE_TYPE_COLOR: Record<string, string> = {
  pdf: 'text-[#ffb786]',
  text: 'text-[#c2c1ff]',
  code: 'text-[#86efac]',
  web: 'text-[#7dd3fc]',
  unknown: 'text-[#c7c4d7]',
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

// ─── 컴포넌트 ──────────────────────────────────────────────────

interface DocumentPreviewRoomProps {
  filePath: string
  onClose?: () => void
  onApprove?: (path: string) => void
}

export function DocumentPreviewRoom({ filePath, onClose, onApprove }: DocumentPreviewRoomProps) {
  const [preview, setPreview] = useState<PreviewResult | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!filePath) return
    setLoading(true)
    setError(null)
    fetch(`${API_BASE}?path=${encodeURIComponent(filePath)}`)
      .then(r => r.json())
      .then(d => {
        setPreview(d)
        setLoading(false)
      })
      .catch(() => {
        setError('미리보기 로드 실패')
        setLoading(false)
      })
  }, [filePath])

  return (
    <div className="flex flex-col h-full bg-[#13131b] text-[#e4e1ed]">
      {/* 헤더 */}
      <div className="flex items-center justify-between px-6 py-4 bg-[#1c1c1e]">
        <div className="flex items-center gap-3">
          <span className="material-symbols-outlined text-[#c2c1ff]">preview</span>
          <div>
            <h2 className="text-sm font-semibold text-[#e4e1ed]">
              {preview?.title ?? '문서 미리보기'}
            </h2>
            {preview && (
              <p className="text-xs text-[#888] mt-0.5">
                <span className={FILE_TYPE_COLOR[preview.file_type] ?? 'text-[#c7c4d7]'}>
                  {FILE_TYPE_LABELS[preview.file_type] ?? preview.file_type}
                </span>
                {preview.page_count !== null && ` · ${preview.page_count}페이지`}
                {' · '}
                {formatFileSize(preview.file_size)}
              </p>
            )}
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#252528] transition-colors text-[#888] hover:text-[#e4e1ed]"
          >
            <span className="material-symbols-outlined text-lg">close</span>
          </button>
        )}
      </div>

      {/* 로딩 */}
      {loading && (
        <div className="flex-1 flex items-center justify-center">
          <span className="material-symbols-outlined animate-spin text-[#5e5ce6] text-3xl">
            progress_activity
          </span>
        </div>
      )}

      {/* 에러 */}
      {!loading && error && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <span className="material-symbols-outlined text-4xl text-[#ffb4ab]">error</span>
          <p className="text-sm text-[#ffb4ab]">{error}</p>
        </div>
      )}

      {/* 미리보기 불가 */}
      {!loading && preview && !preview.available && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <span className="material-symbols-outlined text-4xl text-[#464554]">
            block
          </span>
          <p className="text-sm text-[#888] text-center">
            미리보기를 사용할 수 없습니다.
          </p>
          {preview.error && (
            <p className="text-xs text-[#666] text-center">{preview.error}</p>
          )}
        </div>
      )}

      {/* 미리보기 내용 */}
      {!loading && preview && preview.available && (
        <>
          {/* 민감정보 경고 */}
          {preview.sensitive_flags.length > 0 && (
            <div className="mx-6 mt-4 px-4 py-3 rounded-xl bg-[#502400]/30 flex items-start gap-3">
              <span className="material-symbols-outlined text-[#ffb786] text-lg mt-0.5">
                privacy_tip
              </span>
              <div>
                <p className="text-sm font-medium text-[#ffb786]">민감정보 감지됨</p>
                <p className="text-xs text-[#c7c4d7] mt-0.5">
                  {preview.sensitive_flags.join(', ')} — 민감한 내용이 마스킹 처리됩니다.
                </p>
              </div>
            </div>
          )}

          {/* 파일 경로 */}
          <div className="mx-6 mt-3 px-4 py-2.5 rounded-lg bg-[#1c1c1e] flex items-center gap-2">
            <span className="material-symbols-outlined text-[#888] text-sm">folder</span>
            <span className="text-xs text-[#666] truncate font-mono">{preview.path}</span>
          </div>

          {/* 내용 미리보기 */}
          <div className="flex-1 overflow-y-auto mx-6 mt-3 mb-4">
            <div className="rounded-xl bg-[#1c1c1e] p-5">
              <p className="text-xs text-[#555] mb-3 uppercase tracking-widest font-mono">
                내용 미리보기 (처음 2,000자)
              </p>
              <pre className="text-sm text-[#c7c4d7] whitespace-pre-wrap break-words font-mono leading-relaxed">
                {preview.content_preview || '(미리보기 내용 없음)'}
              </pre>
            </div>
          </div>

          {/* 액션 버튼 */}
          {onApprove && (
            <div className="px-6 pb-6">
              <button
                onClick={() => onApprove(preview.path)}
                className="w-full py-3 rounded-xl bg-[#5e5ce6] hover:bg-[#4d4ad5]
                           text-white font-medium text-sm transition-colors duration-150
                           flex items-center justify-center gap-2"
              >
                <span className="material-symbols-outlined text-sm">check_circle</span>
                이 파일로 작업 진행
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}
