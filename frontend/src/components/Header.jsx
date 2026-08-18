import { Cpu } from 'lucide-react'

export default function Header() {
  return (
    <header className="header">
      <div className="header-logo">
        <Cpu size={20} />
      </div>
      <span className="header-title">Bloomfield Technology</span>
    </header>
  )
}
