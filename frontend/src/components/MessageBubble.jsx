import ToolTrace from './ToolTrace.jsx'
import MarkdownText from './MarkdownText.jsx'

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user'
  return (
    <div className={`message-row ${isUser ? 'from-user' : 'from-assistant'}`}>
      {!isUser && <ToolTrace trace={message.trace} />}
      <div className="bubble">
        {isUser ? message.content : <MarkdownText text={message.content} />}
      </div>
    </div>
  )
}
