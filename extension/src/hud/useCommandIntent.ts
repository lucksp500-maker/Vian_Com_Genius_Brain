/**
 * useCommandIntent — WO-003
 * ActionSpec 생성 hook. Extension HUD에서 사용.
 * POST /api/v1/action-spec/create → action_id + risk_level + guard_result 반환
 */

const API_BASE = 'http://localhost:5051/api/v1/action-spec'

export interface CommandIntentResult {
  actionId: string
  intent: string
  riskLevel: 'none' | 'low' | 'medium' | 'high'
  requiresApproval: boolean
  guardResult: 'allow' | 'deny' | 'ask'
  guardReason: string | null
  executionState: string
  previewUrl: string | null
}

export interface UseCommandIntentState {
  loading: boolean
  error: string | null
  result: CommandIntentResult | null
}

/**
 * Extension HUD에서 사용할 순수 async 함수.
 * React hook 형태이나 Chrome Extension popup에서는 useReducer와 함께 사용.
 */
export async function callCreate(rawInput: string): Promise<CommandIntentResult> {
  const resp = await fetch(`${API_BASE}/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ raw_input: rawInput, source: 'extension' }),
  })

  if (!resp.ok) {
    const text = await resp.text()
    throw new Error(`Backend error ${resp.status}: ${text}`)
  }

  const data = await resp.json() as {
    action_id: string
    intent: string
    risk_level: string
    requires_approval: boolean
    guard_result: string
    guard_reason: string | null
    execution_state: string
    preview_url: string | null
  }

  return {
    actionId: data.action_id,
    intent: data.intent,
    riskLevel: data.risk_level as CommandIntentResult['riskLevel'],
    requiresApproval: data.requires_approval,
    guardResult: data.guard_result as CommandIntentResult['guardResult'],
    guardReason: data.guard_reason,
    executionState: data.execution_state,
    previewUrl: data.preview_url,
  }
}

/**
 * 위험도 > none이면 Web App 새 탭으로 preview URL 열기.
 * Extension background script에서 호출.
 */
export function shouldOpenPreviewTab(result: CommandIntentResult): boolean {
  return result.riskLevel !== 'none' || result.requiresApproval
}
