/**
 * browserCommandRouter.ts — WO-007 (양방향 브리지)
 * Chrome Extension Service Worker (background.js)
 *
 * 양방향 역할:
 *   [수신] 백엔드 명령 큐 폴링 → content script에 EXTRACT_AND_SEND 위임
 *   [송신] content script DOM 추출 결과 → POST /api/v1/browser/result
 *   [직접] Extension 팝업 BROWSER_ACTION 메시지 → POST /api/v1/browser/collect
 *
 * 폴링 흐름 (HUD → Guard → 백엔드 큐 → Extension):
 *   1. 백엔드 GET /api/v1/browser/queue/next → PendingCommand
 *   2. content script 로 EXTRACT_AND_SEND 전송
 *   3. DOM 추출 결과 수신 → POST /api/v1/browser/result
 *
 * 직접 푸시 흐름 (Extension 팝업 클릭):
 *   1. 팝업 → chrome.runtime.sendMessage({type:'BROWSER_ACTION', ...})
 *   2. content script EXTRACT_AND_SEND
 *   3. POST /api/v1/browser/collect
 *
 * [보호] 이유: Extension ↔ Backend 양방향 경계 / 수정 필요 시: BACKEND_URL 또는 POLL_INTERVAL만 수정
 * [의존성] 연결: domContentExtractor.ts / backend browser_automation_adapter.py / 단독 수정 금지
 */

const BACKEND_URL = 'http://localhost:5051'
const QUEUE_ENDPOINT = `${BACKEND_URL}/api/v1/browser/queue/next`
const RESULT_ENDPOINT = `${BACKEND_URL}/api/v1/browser/result`
const COLLECT_ENDPOINT = `${BACKEND_URL}/api/v1/browser/collect`
const PREVIEW_BASE = `${BACKEND_URL}/command-room/preview`

const POLL_INTERVAL_MS = 2000  // 2초마다 큐 폴링

// ─── 타입 ───────────────────────────────────────────────────────

interface PendingCommand {
  command_id: string
  action_type: 'save_tab' | 'summarize' | 'collect'
  action_spec_id: string
}

interface DOMPayload {
  url: string
  title: string
  rawContent: string
  metaDescription: string
  wordCount: number
}

interface PopupMessage {
  type: 'BROWSER_ACTION'
  actionType: 'save_tab' | 'summarize' | 'collect'
}

interface BackendPushResponse {
  action_id?: string
  blocked: boolean
  block_reason: string
  injection_risk: boolean
  intent?: string
  risk_level?: string
  requires_approval?: boolean
  preview_url?: string
}

// ─── 상태 ───────────────────────────────────────────────────────

let _isPolling = false

// ─── 큐 폴링 (백엔드 → Extension 명령 수신) ─────────────────────

async function startPolling(): Promise<void> {
  if (_isPolling) return
  _isPolling = true

  const poll = async () => {
    try {
      const res = await fetch(QUEUE_ENDPOINT)
      if (res.status === 200) {
        const cmd: PendingCommand = await res.json()
        await executeCommand(cmd)
      }
      // 204 No Content = 큐 비어있음, 계속 폴링
    } catch {
      // 네트워크 오류 무시 (백엔드 미시작 상태 허용)
    }
    setTimeout(poll, POLL_INTERVAL_MS)
  }

  poll()
}

// ─── 명령 실행 (큐에서 꺼낸 명령) ──────────────────────────────

async function executeCommand(cmd: PendingCommand): Promise<void> {
  // 활성 탭에 content script 메시지 전송
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
  const tab = tabs[0]
  if (!tab?.id) return

  let domPayload: DOMPayload | null = null

  try {
    const response = await chrome.tabs.sendMessage(tab.id, {
      type: 'EXTRACT_AND_SEND',
      actionType: cmd.action_type,
    }) as { ok: boolean; result?: DOMPayload; error?: string }

    if (response?.ok && response.result) {
      domPayload = response.result
    }
  } catch {
    // content script 미주입 탭 (chrome://, extension:// 등) — 무시
    return
  }

  if (!domPayload) return

  // DOM 결과 → 백엔드 전송
  await fetch(RESULT_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      command_id: cmd.command_id,
      action_type: cmd.action_type,
      url: domPayload.url,
      title: domPayload.title,
      raw_content: domPayload.rawContent,
      meta_description: domPayload.metaDescription,
      word_count: domPayload.wordCount,
    }),
  })

  // 결과 저장 (팝업 표시용)
  await chrome.storage.session.set({
    lastBrowserResult: {
      command_id: cmd.command_id,
      action_type: cmd.action_type,
      queued: true,
    },
  })
}

// ─── 직접 푸시 (팝업 클릭 → 백엔드 collect) ────────────────────

async function handleDirectPush(
  actionType: 'save_tab' | 'summarize' | 'collect'
): Promise<BackendPushResponse> {
  const tabs = await chrome.tabs.query({ active: true, currentWindow: true })
  const tab = tabs[0]
  if (!tab?.id) {
    return { blocked: true, block_reason: '활성 탭 없음', injection_risk: false }
  }

  let domPayload: DOMPayload | null = null

  try {
    const response = await chrome.tabs.sendMessage(tab.id, {
      type: 'EXTRACT_AND_SEND',
      actionType,
    }) as { ok: boolean; payload?: DOMPayload; error?: string }

    if (response?.ok && response.payload) {
      domPayload = response.payload
    }
  } catch {
    return { blocked: true, block_reason: 'Content script 응답 없음', injection_risk: false }
  }

  if (!domPayload) {
    return { blocked: true, block_reason: 'DOM 추출 실패', injection_risk: false }
  }

  const res = await fetch(COLLECT_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      action_type: actionType,
      url: domPayload.url,
      title: domPayload.title,
      raw_content: domPayload.rawContent,
      meta_description: domPayload.metaDescription,
      word_count: domPayload.wordCount,
    }),
  })

  if (!res.ok) {
    return { blocked: true, block_reason: `Backend ${res.status}`, injection_risk: false }
  }

  const data: BackendPushResponse = await res.json()

  // 승인 필요 → 새 탭 Preview
  if (!data.blocked && data.requires_approval && data.action_id) {
    const url = data.preview_url || `${PREVIEW_BASE}/${data.action_id}`
    await chrome.tabs.create({ url })
  }

  await chrome.storage.session.set({ lastBrowserResult: data })
  return data
}

// ─── 팝업 메시지 리스너 ──────────────────────────────────────────

chrome.runtime.onMessage.addListener(
  (message: PopupMessage, _sender, sendResponse) => {
    if (message.type !== 'BROWSER_ACTION') return false

    handleDirectPush(message.actionType)
      .then((result) => sendResponse({ ok: true, result }))
      .catch((err) => sendResponse({ ok: false, error: String(err) }))

    return true // 비동기 sendResponse 허용
  }
)

// ─── 서비스 워커 시작 ────────────────────────────────────────────

chrome.runtime.onInstalled.addListener(() => {
  startPolling()
})

chrome.runtime.onStartup.addListener(() => {
  startPolling()
})

// 서비스 워커 활성화 시 즉시 폴링 시작
startPolling()
