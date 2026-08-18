import { MessageCircle, X } from 'lucide-react'

export default function ChatFab({ open, onClick }) {
  return (
    <button className={`chat-fab${open ? ' open' : ''}`} aria-label="Open chat" onClick={onClick}>
      <MessageCircle className="icon-open" />
      <X className="icon-close" />
    </button>
  )
}
