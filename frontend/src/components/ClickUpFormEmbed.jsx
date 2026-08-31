export default function ClickUpFormEmbed({ src, title, height = '1400px' }) {
  return (
    <div className="form-embed">
      <iframe src={src} title={title} width="100%" height={height} loading="lazy" />
      <p className="form-embed-fallback">
        Form not loading?{' '}
        <a href={src} target="_blank" rel="noopener noreferrer">
          Open it in a new tab
        </a>
        .
      </p>
    </div>
  )
}
