import { Link } from 'react-router-dom'
import { ExternalLink } from 'lucide-react'

export default function ServiceCard({ to, icon: Icon, title, desc, badge, variant, external }) {
  const className = variant ? `service-link ${variant}` : 'service-link'
  const content = (
    <>
      <div className="service-icon">
        <Icon />
      </div>
      <div className="service-text">
        <h3>
          {title}
          {badge && <span className="service-badge">{badge}</span>}
          {external && <ExternalLink className="service-external-icon" aria-hidden="true" />}
        </h3>
        <p>{desc}</p>
      </div>
    </>
  )

  if (external) {
    return (
      <a href={to} className={className} target="_blank" rel="noopener noreferrer">
        {content}
      </a>
    )
  }

  return (
    <Link to={to} className={className}>
      {content}
    </Link>
  )
}
