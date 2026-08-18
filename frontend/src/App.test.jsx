import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it } from 'vitest'
import App from './App.jsx'

function renderAt(path) {
  return render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  )
}

describe('App routing', () => {
  it('renders the landing page at /', () => {
    renderAt('/')
    expect(screen.getByText('How can we help you today?')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /open chat/i })).toBeInTheDocument()
  })

  it('renders the internal agent view at /agent', () => {
    renderAt('/agent')
    expect(screen.getByText('ClickUp Agent')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /open chat/i })).toBeInTheDocument()
  })

  it('renders all five service links on the landing page', () => {
    renderAt('/')
    expect(screen.getByText('WiFi Your Phone')).toBeInTheDocument()
    expect(screen.getByText('Request Tech Support')).toBeInTheDocument()
    expect(screen.getByText('Tech-ED Training')).toBeInTheDocument()
    expect(screen.getByText('ID Request')).toBeInTheDocument()
    expect(screen.getByText('Media Specialist Portal')).toBeInTheDocument()
  })

  it.each([
    ['/wifi-request', 'WiFi Your Phone'],
    ['/ticket-request', 'Request Tech Support'],
    ['/training-request', 'Tech-ED Training'],
    ['/id-request', 'ID Request'],
    ['/media-specialist-helpdesk', 'Media Specialist Portal'],
  ])('resolves the stub route %s', (path, heading) => {
    renderAt(path)
    expect(screen.getByText(heading)).toBeInTheDocument()
  })
})
