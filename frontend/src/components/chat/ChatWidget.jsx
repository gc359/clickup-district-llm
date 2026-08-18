import { useRef, useState } from 'react'
import ChatFab from './ChatFab.jsx'
import ChatPanel from './ChatPanel.jsx'
import { postWidgetChat } from '../../api.js'

let nextId = 1

const GREETING =
  "Hey! I'm Helpdesk Hero. I can troubleshoot IT issues or submit a support ticket for you. What do you need help with?"

export default function ChatWidget() {
  const sessionIdRef = useRef(null)
  if (sessionIdRef.current === null) {
    sessionIdRef.current = crypto.randomUUID()
  }

  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState([{ id: nextId++, type: 'bot', text: GREETING }])
  const [showQuickReplies, setShowQuickReplies] = useState(true)
  const [formVisible, setFormVisible] = useState(false)
  const [typing, setTyping] = useState(false)

  function addMessage(type, text) {
    setMessages((prev) => [...prev, { id: nextId++, type, text }])
  }

  async function sendMessage(text) {
    if (!text.trim()) return
    addMessage('user', text)
    setTyping(true)
    try {
      const response = await postWidgetChat(sessionIdRef.current, text)
      setTyping(false)
      addMessage('bot', response.text || 'I encountered an issue. Please try again.')
    } catch {
      setTyping(false)
      addMessage(
        'bot',
        "I'm having trouble connecting right now. You can submit a ticket using the form above or try again in a moment.",
      )
    }
  }

  function handleQuickReply(reply) {
    setShowQuickReplies(false)
    if (reply.action === 'show-form') {
      addMessage('user', 'I want to submit a ticket')
      setFormVisible(true)
      return
    }
    sendMessage(reply.msg)
  }

  function handleFormCancel() {
    setFormVisible(false)
    addMessage('bot', 'No problem. Let me know if you need anything else!')
  }

  function handleFormSubmitted(ticket) {
    setFormVisible(false)
    addMessage('system', '✓ Ticket submitted successfully!')
    addMessage(
      'bot',
      `Your ticket has been created (ID: ${ticket.id || 'pending'}). Our team will follow up with you. Anything else I can help with?`,
    )
  }

  function handleFormError() {
    addMessage('system', '⚠ Failed to submit. Please try again or contact IT directly.')
  }

  return (
    <>
      <ChatFab open={open} onClick={() => setOpen((prev) => !prev)} />
      <ChatPanel
        open={open}
        messages={messages}
        showQuickReplies={showQuickReplies}
        formVisible={formVisible}
        typing={typing}
        onQuickReply={handleQuickReply}
        onSend={sendMessage}
        onFormCancel={handleFormCancel}
        onFormSubmitted={handleFormSubmitted}
        onFormError={handleFormError}
      />
    </>
  )
}
