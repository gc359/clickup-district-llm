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

    expect(screen.getByRole('heading', { name: 'Alpha' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Building Status' })).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Submit a ticket' })).toBeInTheDocument()
  })

  it('sends a quick reply and renders the widget-scoped chat response', async () => {
    api.postWidgetChat.mockResolvedValueOnce({
      text: 'All buildings are open on a normal schedule.',
      trace: [],
      stopped_reason: 'complete',
    })

    const user = userEvent.setup()
    render(<ChatWidget />)

    await user.click(screen.getByRole('button', { name: /open chat/i }))
    await user.click(screen.getByRole('button', { name: 'Building Status' }))

    expect(screen.getByText('What is the current building status?')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByText('All buildings are open on a normal schedule.')).toBeInTheDocument()
    })
    expect(api.postWidgetChat).toHaveBeenCalledWith(
      expect.any(String),
      'What is the current building status?',
    )
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
