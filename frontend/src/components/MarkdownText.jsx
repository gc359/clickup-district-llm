import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

// No rehype-raw / dangerouslySetInnerHTML anywhere here on purpose: react-markdown
// parses Markdown straight into React elements, so any literal "<script>" or
// "<img onerror=...>" text coming back from the LLM renders as inert text instead
// of being interpreted as HTML.
export default function MarkdownText({ text }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      disallowedElements={['img']}
      unwrapDisallowed
      components={{
        a: ({ node, ...props }) => (
          <a {...props} target="_blank" rel="noopener noreferrer" />
        ),
      }}
    >
      {text}
    </ReactMarkdown>
  )
}
