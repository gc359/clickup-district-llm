import { useRef, useState } from 'react'
import MessageList from '../components/MessageList.jsx'
import Composer from '../components/Composer.jsx'
import { postChat } from '../api.js'

let nextId = 1

export default function Agent() {
  const sessionIdRef = useRef(null)
  if (sessionIdRef.current === null) {
    sessionIdRef.current = crypto.randomUUID()
  }

  const [messages, setMessages] = useState([])
  const [pending, setPending] = useState(false)
  const [error, setError] = useState(null)

  async function handleSend(text) {
    setError(null)
    setMessages((prev) => [...prev, { id: nextId++, role: 'user', content: text }])
    setPending(true)
    try {
      const response = await postChat(sessionIdRef.current, text)
      setMessages((prev) => [
        ...prev,
        { id: nextId++, role: 'assistant', content: response.text, trace: response.trace },
      ])
    } catch (err) {
      setError(err.message)
    } finally {
      setPending(false)
    }
  }

  return (
    <div className="app">
      <header className="app-header">
        <h1>ClickUp Agent</h1>
      </header>
      <MessageList messages={messages} />
      {pending && (
        <div className="pending-banner">Thinking… this can take 5–20s on local models.</div>
      )}
      {error && <div className="error-banner">{error}</div>}
      <Composer onSend={handleSend} pending={pending} />
    </div>
  )
}
