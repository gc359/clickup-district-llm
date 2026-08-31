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
    ['/wifi-request', 'WiFi Your Phone', 'https://forms.clickup.com/9014421433/f/8cmu9xt-10274/1Y9ZK3KUWYES4VUMK9'],
    ['/ticket-request', 'Request Tech Support', 'https://forms.clickup.com/9014421433/f/8cmu9xt-1394/VD6ZUUD0H5MCHPEH3R'],
    ['/training-request', 'Tech-ED Training', 'https://forms.clickup.com/9014421433/f/8cmu9xt-8714/SI4KA8USV49RXV9RXR'],
    ['/id-request', 'ID Request', 'https://forms.clickup.com/9014421433/f/8cmu9xt-10294/LE7CAQHAKESP6J0KSD'],
    ['/chromebook-repair', 'Media Specialist Chromebook Repair', 'https://forms.clickup.com/9014421433/f/8cmu9xt-14274/487EVW1HFMQEO835RS'],
  ])('renders the %s form page with a working embed', (path, heading, formSrc) => {
    renderAt(path)
    expect(screen.getByRole('heading', { level: 1, name: heading })).toBeInTheDocument()
    expect(screen.getByTitle(`${heading} form`)).toHaveAttribute('src', formSrc)
  })

  it('renders the media specialist hub with an internal repair link and an external device-request link', () => {
    renderAt('/media-specialist-helpdesk')
    expect(screen.getByRole('heading', { level: 1, name: 'Chromebook Helpdesk' })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Chromebook Repair/i })).toHaveAttribute('href', '/chromebook-repair')
    const deviceLink = screen.getByRole('link', { name: /New\/Replacement Device/i })
    expect(deviceLink).toHaveAttribute(
      'href',
      'https://bloomfieldk12.clickup.com/forms/9014421433/f/8cmu9xt-23694/MFLD5VDFT3651RIJ64',
    )
    expect(deviceLink).toHaveAttribute('target', '_blank')
  })
})
