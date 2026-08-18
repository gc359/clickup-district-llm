import { Wifi, LifeBuoy, GraduationCap, IdCard, Laptop } from 'lucide-react'
import ServiceCard from './ServiceCard.jsx'

const SERVICES = [
  {
    to: '/wifi-request',
    icon: Wifi,
    title: 'WiFi Your Phone',
    desc: 'Connect your personal device to the district network',
  },
  {
    to: '/ticket-request',
    icon: LifeBuoy,
    title: 'Request Tech Support',
    desc: 'Submit a ticket for hardware, software, or account issues',
  },
  {
    to: '/training-request',
    icon: GraduationCap,
    title: 'Tech-ED Training',
    desc: 'Request technology training or professional development',
  },
  {
    to: '/id-request',
    icon: IdCard,
    title: 'ID Request',
    desc: 'Order a new or replacement staff or student ID badge',
  },
  {
    to: '/media-specialist-helpdesk',
    icon: Laptop,
    title: 'Media Specialist Portal',
    desc: 'Chromebook repairs and device requests for librarians',
    badge: 'Staff',
    variant: 'media-specialist',
  },
]

export default function ServicesGrid() {
  return (
    <div className="services">
      {SERVICES.map((service) => (
        <ServiceCard key={service.to} {...service} />
      ))}
    </div>
  )
}
