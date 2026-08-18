import MarkdownText from '../MarkdownText.jsx'

export default function WidgetMessage({ type, text, children }) {
  return (
    <div className={`msg ${type}`}>
      {type === 'bot' ? <MarkdownText text={text} /> : text}
      {children}
    </div>
  )
}
