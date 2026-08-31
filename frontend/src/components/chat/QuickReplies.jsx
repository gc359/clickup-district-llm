const REPLIES = [
  { label: 'Building Status', msg: 'What is the current building status?' },
  { label: 'District Phone Directory', msg: 'I need the district phone directory' },
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
