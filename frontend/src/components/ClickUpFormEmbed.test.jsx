import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import ClickUpFormEmbed from './ClickUpFormEmbed.jsx'

describe('ClickUpFormEmbed', () => {
  it('renders an iframe with the given src and accessible title', () => {
    render(<ClickUpFormEmbed src="https://forms.clickup.com/x" title="Test form" />)
    const iframe = screen.getByTitle('Test form')
    expect(iframe.tagName).toBe('IFRAME')
    expect(iframe).toHaveAttribute('src', 'https://forms.clickup.com/x')
    expect(iframe).toHaveAttribute('height', '1400px')
  })

  it('renders a fallback link to open the form in a new tab', () => {
    render(<ClickUpFormEmbed src="https://forms.clickup.com/x" title="Test form" />)
    expect(screen.getByRole('link', { name: /open it in a new tab/i })).toHaveAttribute(
      'href',
      'https://forms.clickup.com/x',
    )
  })
})
