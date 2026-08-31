export default function Hero({
  title = 'How can we help you today?',
  description = 'The Bloomfield Technology Department handles hardware, software, security, and data management to keep our district running on a secure, efficient system.',
}) {
  return (
    <div className="hero">
      <h1>{title}</h1>
      <p>{description}</p>
    </div>
  )
}
