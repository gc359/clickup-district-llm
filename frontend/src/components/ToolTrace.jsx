function iconFor(entry) {
  if (!entry.ok) return '❌'
  return entry.tool === 'create_task' ? '✅' : '🔍'
}

export default function ToolTrace({ trace }) {
  if (!trace || trace.length === 0) return null

  return (
    <div className="tool-trace">
      {trace.map((entry, i) => (
        <span key={i} className={`chip ${entry.ok ? 'chip-ok' : 'chip-error'}`}>
          {iconFor(entry)} {entry.tool}
        </span>
      ))}
    </div>
  )
}
