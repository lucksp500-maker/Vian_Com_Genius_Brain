/**
 * domContentExtractor.ts — WO-007
 * Chrome Extension Content Script (content.js)
 *
 * 역할:
 *   background service worker의 EXTRACT_AND_SEND 메시지를 받아
 *   현재 페이지 DOM에서 텍스트 본문과 메타데이터를 추출하여 반환합니다.
 *
 * 보안 원칙:
 *   - DOM 읽기 전용 — 수정 없음
 *   - password 입력 필드 값 수집 안함
 *   - 추출된 텍스트는 백엔드 PromptInjectionShield에서 재검사
 *
 * 흐름:
 *   background SW → chrome.tabs.sendMessage({type:'EXTRACT_AND_SEND', actionType})
 *     → extractDOMContent()
 *     → sendResponse({ ok: true, payload: DOMPayload })
 *
 * [보호] 이유: 브라우저 데이터 수집 경계 / 수정 필요 시: extractDOMContent()만 수정
 * [의존성] 연결: browserCommandRouter.ts / 단독 수정 금지
 */

const MAX_CONTENT_CHARS = 8000

// ─── 타입 ───────────────────────────────────────────────────────

interface DOMPayload {
  url: string
  title: string
  rawContent: string
  metaDescription: string
  wordCount: number
}

// ─── DOM 추출 ───────────────────────────────────────────────────

function extractDOMContent(): DOMPayload {
  const url = window.location.href
  const title = document.title || ''

  const metaEl = document.querySelector<HTMLMetaElement>('meta[name="description"]')
  const metaDescription = metaEl?.content || ''

  // 스크립트/스타일/숨겨진 요소 제거 후 텍스트 추출
  const clone = document.body.cloneNode(true) as HTMLElement
  const removeSelectors = [
    'script', 'style', 'noscript',
    '[style*="display:none"]', '[style*="visibility:hidden"]',
    '[aria-hidden="true"]', 'input[type="password"]',
  ]
  removeSelectors.forEach((sel) => {
    clone.querySelectorAll(sel).forEach((el) => el.remove())
  })

  let rawContent = (clone.innerText || clone.textContent || '')
    .replace(/\s{3,}/g, '\n\n')
    .replace(/\t+/g, ' ')
    .trim()

  if (rawContent.length > MAX_CONTENT_CHARS) {
    rawContent = rawContent.slice(0, MAX_CONTENT_CHARS) + '\n[이하 내용 생략]'
  }

  const wordCount = rawContent.split(/\s+/).filter(Boolean).length

  return { url, title, rawContent, metaDescription, wordCount }
}

// ─── 메시지 리스너 ──────────────────────────────────────────────

chrome.runtime.onMessage.addListener(
  (
    message: { type: string; actionType?: string },
    _sender,
    sendResponse: (response: { ok: boolean; payload?: DOMPayload; error?: string }) => void
  ) => {
    if (message.type !== 'EXTRACT_AND_SEND') return false

    try {
      const payload = extractDOMContent()
      sendResponse({ ok: true, payload })
    } catch (err) {
      sendResponse({ ok: false, error: String(err) })
    }

    return true
  }
)
