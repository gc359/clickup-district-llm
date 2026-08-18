import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import TicketForm from './TicketForm.jsx'
import * as api from '../../api.js'

vi.mock('../../api.js')

describe('TicketForm', () => {
  beforeEach(() => {
    vi.spyOn(window, 'alert').mockImplementation(() => {})
  })

  it('alerts and does not submit when name/description are missing', async () => {
    const onSubmitted = vi.fn()
    const user = userEvent.setup()
    render(<TicketForm onCancel={vi.fn()} onSubmitted={onSubmitted} onError={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'Submit Ticket' }))

    expect(window.alert).toHaveBeenCalledWith('Please fill in your name and a description.')
    expect(api.postTicket).not.toHaveBeenCalled()
    expect(onSubmitted).not.toHaveBeenCalled()
  })

  it('submits valid data and reports the created ticket', async () => {
    api.postTicket.mockResolvedValueOnce({ id: 't1', url: 'https://x', status: 'created' })
    const onSubmitted = vi.fn()
    const user = userEvent.setup()
    render(<TicketForm onCancel={vi.fn()} onSubmitted={onSubmitted} onError={vi.fn()} />)

    await user.type(screen.getByLabelText('Your Name'), 'Jane Doe')
    await user.type(screen.getByLabelText('Description'), "Can't connect to WiFi")
    await user.click(screen.getByRole('button', { name: 'Submit Ticket' }))

    await waitFor(() => expect(onSubmitted).toHaveBeenCalledWith({ id: 't1', url: 'https://x', status: 'created' }))
    expect(api.postTicket).toHaveBeenCalledWith(
      expect.objectContaining({ name: 'Jane Doe', description: "Can't connect to WiFi", category: 'Other' }),
    )
  })

  it('calls onCancel when the cancel button is clicked', async () => {
    const onCancel = vi.fn()
    const user = userEvent.setup()
    render(<TicketForm onCancel={onCancel} onSubmitted={vi.fn()} onError={vi.fn()} />)

    await user.click(screen.getByRole('button', { name: 'Cancel' }))

    expect(onCancel).toHaveBeenCalled()
  })

  it('re-enables the submit button and calls onError on failure', async () => {
    api.postTicket.mockRejectedValueOnce(new Error('Request failed with status 502'))
    const onError = vi.fn()
    const user = userEvent.setup()
    render(<TicketForm onCancel={vi.fn()} onSubmitted={vi.fn()} onError={onError} />)

    await user.type(screen.getByLabelText('Your Name'), 'Jane Doe')
    await user.type(screen.getByLabelText('Description'), 'Broken laptop')
    await user.click(screen.getByRole('button', { name: 'Submit Ticket' }))

    await waitFor(() => expect(onError).toHaveBeenCalled())
    expect(screen.getByRole('button', { name: 'Submit Ticket' })).not.toBeDisabled()
  })
})
