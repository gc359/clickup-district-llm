import { Link } from 'react-router-dom'

export default function ComingSoon({ title, description }) {
  return (
    <div className="hero">
      <h1>{title}</h1>
      <p>{description}</p>
      <p style={{ marginTop: '1.5rem' }}>
        <Link to="/">&larr; Back to home</Link>
      </p>
    </div>
  )
}
