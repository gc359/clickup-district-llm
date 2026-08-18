const REPLIES = [
  { label: 'WiFi help', msg: 'I need WiFi help' },
  { label: 'Password reset', msg: 'My password needs to be reset' },
  { label: 'Printer issue', msg: 'I have a printer issue' },
  { label: 'Submit a ticket', action: 'show-form' },
]

export default function QuickReplies({ onSelect }) {
  return (
    <div className="quick-replies">
      {REPLIES.map((reply) => (
        <button key={reply.label} className="quick-reply" onClick={() => onSelect(reply)}>
          {reply.label}
        </button>
      ))}
    </div>
  )
}
