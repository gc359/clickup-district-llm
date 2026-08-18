import { useState } from 'react'

export default function Composer({ onSend, pending }) {
  const [value, setValue] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    const trimmed = value.trim()
    if (!trimmed || pending) return
    onSend(trimmed)
    setValue('')
  }

  return (
    <form className="composer" onSubmit={handleSubmit}>
      <input
        type="text"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder="Ask about your ClickUp workspace..."
        disabled={pending}
        aria-label="Message"
      />
      <button type="submit" disabled={pending || !value.trim()}>
        {pending ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}
