/**
 * LocalSearchResultViewer — WO-004
 * 로컬 파일 색인 검색 UI.
 * LocalIndexer(backend)에 검색 요청 → 결과 카드 표시 → DocumentPreviewRoom 연결.
 *
 * 흐름: 사용자 검색 입력 → GET /api/v1/local-index/search?q=... → 결과 목록
 *        → 항목 클릭 → /command-room/preview-local/:encodedPath
 */
import { useEffect, useState, useCallback } from 'react'

const API_BASE = '/api/v1/local-index'

// ─── 타입 정의 ──────────────────────────────────────────────────

interface IndexedItem {
  item_id: string
  path: string
  title: string
  file_type: string
  last_modified: number
  file_size: number
  summary: string
  sensitive_flags: string
  indexed_at: number
}

// ─── 헬퍼 ───────────────────────────────────────────────────────

const FILE_TYPE_ICON: Record<string, string> = {
  pdf: 'picture_as_pdf',
  text: 'description',
  code: 'code',
  web: 'language',
  unknown: 'insert_drive_file',
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

function formatDate(timestamp: number): string {
  return new Date(timestamp * 1000).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  })
}

// ─── 컴포넌트 ──────────────────────────────────────────────────

interface LocalSearchResultViewerProps {
  onSelectFile?: (path: string) => void
}

export function LocalSearchResultViewer({ onSelectFile }: LocalSearchResultViewerProps) {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<IndexedItem[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [indexed, setIndexed] = useState(false)
  const [indexing, setIndexing] = useState(false)
  const [totalCount, setTotalCount] = useState<number | null>(null)

  // 초기 색인 실행 여부 확인
  useEffect(() => {
    fetch(`${API_BASE}/count`)
      .then(r => r.json())
      .then(d => {
        if (d.count > 0) {
          setIndexed(true)
          setTotalCount(d.count)
          // 빈 쿼리로 최근 항목 불러오기
          fetchResults('')
        }
      })
      .catch(() => setError('색인 상태 확인 실패'))
  }, [])

  const fetchResults = useCallback((q: string) => {
    setLoading(true)
    setError(null)
    fetch(`${API_BASE}/search?q=${encodeURIComponent(q)}&limit=30`)
      .then(r => r.json())
      .then(d => {
        setResults(d.results ?? [])
        setLoading(false)
      })
      .catch(() => {
        setError('검색 요청 실패')
        setLoading(false)
      })
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    fetchResults(query)
  }

  const handleIndex = () => {
    setIndexing(true)
    fetch(`${API_BASE}/index`, { method: 'POST' })
      .then(r => r.json())
      .then(d => {
        setIndexed(true)
        setTotalCount(d.indexed_count)
        setIndexing(false)
        fetchResults(query)
      })
      .catch(() => {
        setError('색인 실패')
        setIndexing(false)
      })
  }

  const handleSelectFile = (item: IndexedItem) => {
    if (onSelectFile) {
      onSelectFile(item.path)
    }
  }

  return (
    <div className="flex flex-col h-full bg-[#13131b] text-[#e4e1ed]">
      {/* 헤더 */}
      <div className="px-6 pt-6 pb-4 bg-[#1c1c1e]">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="material-symbols-outlined text-[#c2c1ff] text-2xl">
              manage_search
            </span>
            <div>
              <h2 className="text-base font-semibold text-[#e4e1ed] tracking-tight">
                로컬 파일 검색
              </h2>
              {totalCount !== null && (
                <p className="text-xs text-[#888] mt-0.5">{totalCount.toLocaleString()}개 파일 색인됨</p>
              )}
            </div>
          </div>
          <button
            onClick={handleIndex}
            disabled={indexing}
            className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#5e5ce6] hover:bg-[#4d4ad5]
                       text-white text-xs font-medium transition-colors duration-150
                       disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span className="material-symbols-outlined text-sm">
              {indexing ? 'sync' : 'folder_sync'}
            </span>
            {indexing ? '색인 중...' : '색인 갱신'}
          </button>
        </div>

        {/* 검색창 */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <div className="flex-1 relative">
            <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-[#888] text-lg">
              search
            </span>
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="파일 이름, 내용으로 검색..."
              className="w-full pl-10 pr-4 py-2.5 bg-[#252528] rounded-lg text-sm text-[#e4e1ed]
                         placeholder:text-[#555] outline-none focus:ring-1 focus:ring-[#5e5ce6]
                         transition-all duration-150"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-4 py-2.5 rounded-lg bg-[#5e5ce6] hover:bg-[#4d4ad5] text-white text-sm
                       font-medium transition-colors duration-150 disabled:opacity-50"
          >
            검색
          </button>
        </form>
      </div>

      {/* 에러 배너 */}
      {error && (
        <div className="mx-6 mt-3 px-4 py-2.5 rounded-lg bg-[#93000a]/20 text-[#ffb4ab] text-sm flex items-center gap-2">
          <span className="material-symbols-outlined text-sm">error</span>
          {error}
        </div>
      )}

      {/* 미색인 안내 */}
      {!indexed && !indexing && (
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <span className="material-symbols-outlined text-5xl text-[#464554]">folder_open</span>
          <p className="text-sm text-[#888] text-center">
            아직 파일을 색인하지 않았습니다.
            <br />색인 갱신 버튼을 눌러 로컬 파일을 검색 가능하게 만드세요.
          </p>
        </div>
      )}

      {/* 검색 결과 목록 */}
      {indexed && (
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-2">
          {loading && (
            <div className="flex items-center justify-center py-8">
              <span className="material-symbols-outlined animate-spin text-[#5e5ce6]">progress_activity</span>
            </div>
          )}

          {!loading && results.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 gap-3">
              <span className="material-symbols-outlined text-4xl text-[#464554]">search_off</span>
              <p className="text-sm text-[#888]">검색 결과가 없습니다.</p>
            </div>
          )}

          {!loading && results.map(item => (
            <button
              key={item.item_id}
              onClick={() => handleSelectFile(item)}
              className="w-full text-left px-4 py-3 rounded-xl bg-[#1c1c1e] hover:bg-[#252528]
                         transition-colors duration-150 group"
            >
              <div className="flex items-start gap-3">
                <span className={`material-symbols-outlined mt-0.5 ${FILE_TYPE_COLOR[item.file_type] ?? 'text-[#c7c4d7]'}`}>
                  {FILE_TYPE_ICON[item.file_type] ?? 'insert_drive_file'}
                </span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-sm font-medium text-[#e4e1ed] truncate group-hover:text-white">
                      {item.title}
                    </span>
                    <span className="text-xs text-[#555] shrink-0">
                      {formatFileSize(item.file_size)}
                    </span>
                  </div>
                  <p className="text-xs text-[#888] mt-0.5 truncate">{item.path}</p>
                  {item.summary && (
                    <p className="text-xs text-[#666] mt-1 line-clamp-1">{item.summary}</p>
                  )}
                  <div className="flex items-center gap-3 mt-1.5">
                    <span className="text-[10px] text-[#555]">{formatDate(item.last_modified)}</span>
                    {item.sensitive_flags && (
                      <span className="text-[10px] text-[#ffb786] flex items-center gap-1">
                        <span className="material-symbols-outlined text-[10px]">warning</span>
                        민감정보 감지
                      </span>
                    )}
                  </div>
                </div>
                <span className="material-symbols-outlined text-[#464554] group-hover:text-[#5e5ce6] text-sm transition-colors">
                  arrow_forward
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
