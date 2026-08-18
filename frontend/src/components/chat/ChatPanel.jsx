import { useEffect, useRef, useState } from 'react'
import { Bot, Send } from 'lucide-react'
import WidgetMessage from './WidgetMessage.jsx'
import QuickReplies from './QuickReplies.jsx'
import TypingIndicator from './TypingIndicator.jsx'
import TicketForm from './TicketForm.jsx'

export default function ChatPanel({
  open,
  messages,
  showQuickReplies,
  formVisible,
  typing,
  onQuickReply,
  onSend,
  onFormCancel,
  onFormSubmitted,
  onFormError,
}) {
  const [value, setValue] = useState('')
  const textareaRef = useRef(null)

  useEffect(() => {
    if (open) textareaRef.current?.focus()
  }, [open])

  function handleInput(e) {
    setValue(e.target.value)
    const el = textareaRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 100)}px`
    }
  }

  function submit() {
    const text = value.trim()
    if (!text) return
    onSend(text)
    setValue('')
    if (textareaRef.current) textareaRef.current.style.height = 'auto'
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <div className={`chat-panel${open ? ' open' : ''}`}>
      <div className="chat-header">
        <div className="chat-avatar">
          <Bot />
        </div>
        <div className="chat-header-info">
          <h2>Helpdesk Hero</h2>
          <p>AI Tech Support</p>
        </div>
        <div className="chat-status" title="Online" />
      </div>

      <div className="chat-messages">
        {messages.map((message, index) => (
          <WidgetMessage key={message.id} type={message.type} text={message.text}>
            {index === 0 && showQuickReplies && <QuickReplies onSelect={onQuickReply} />}
          </WidgetMessage>
        ))}
        {formVisible && (
          <TicketForm onCancel={onFormCancel} onSubmitted={onFormSubmitted} onError={onFormError} />
        )}
        {typing && <TypingIndicator />}
      </div>

      <div className="chat-input-area">
        <textarea
          ref={textareaRef}
          className="chat-input"
          rows={1}
          placeholder="Describe your issue..."
          value={value}
          onChange={handleInput}
          onKeyDown={handleKeyDown}
        />
        <button className="chat-send" aria-label="Send message" onClick={submit}>
          <Send />
        </button>
      </div>
    </div>
  )
}
