import { Link } from 'react-router-dom'

export default function ServiceCard({ to, icon: Icon, title, desc, badge, variant }) {
  const className = variant ? `service-link ${variant}` : 'service-link'

  return (
    <Link to={to} className={className}>
      <div className="service-icon">
        <Icon />
      </div>
      <div className="service-text">
        <h3>
          {title}
          {badge && <span className="service-badge">{badge}</span>}
        </h3>
        <p>{desc}</p>
      </div>
    </Link>
  )
}
