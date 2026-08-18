import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import ChatWidget from './ChatWidget.jsx'
import * as api from '../../api.js'

vi.mock('../../api.js')

describe('ChatWidget', () => {
  it('opens the panel and shows the greeting with quick replies', async () => {
    const user = userEvent.setup()
    render(<ChatWidget />)

    await user.click(screen.getByRole('button', { name: /open chat/i }))

    expect(screen.getByRole('heading', { name: 'Helpdesk Hero' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'WiFi help' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Submit a ticket' })).toBeInTheDocument()
  })

  it('sends a quick reply and renders the widget-scoped chat response', async () => {
    api.postWidgetChat.mockResolvedValueOnce({
      text: 'Try forgetting the network and reconnecting.',
      trace: [],
      stopped_reason: 'complete',
    })

    const user = userEvent.setup()
    render(<ChatWidget />)

    await user.click(screen.getByRole('button', { name: /open chat/i }))
    await user.click(screen.getByRole('button', { name: 'WiFi help' }))

    expect(screen.getByText('I need WiFi help')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('Try forgetting the network and reconnecting.')).toBeInTheDocument()
    })
    expect(api.postWidgetChat).toHaveBeenCalledWith(expect.any(String), 'I need WiFi help')
  })

  it('opens the ticket form from the "Submit a ticket" quick reply', async () => {
    const user = userEvent.setup()
    render(<ChatWidget />)

    await user.click(screen.getByRole('button', { name: /open chat/i }))
    await user.click(screen.getByRole('button', { name: 'Submit a ticket' }))

    expect(screen.getByText('I want to submit a ticket')).toBeInTheDocument()
    expect(screen.getByText('Submit a Support Ticket')).toBeInTheDocument()
  })
})
