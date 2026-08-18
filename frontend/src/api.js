const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

async function _postJSON(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

  if (!response.ok) {
    let detail = `Request failed with status ${response.status}`
    try {
      const responseBody = await response.json()
      if (responseBody.detail) detail = JSON.stringify(responseBody.detail)
    } catch {
      // response wasn't JSON — keep the default detail
    }
    throw new Error(detail)
  }

  return response.json()
}

export async function postChat(sessionId, message) {
  return _postJSON('/chat', { session_id: sessionId, message })
}

export async function postWidgetChat(sessionId, message) {
  return _postJSON('/api/chat', { session_id: sessionId, message })
}

export async function postTicket(payload) {
  return _postJSON('/api/ticket', payload)
}
