import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import Agent from './Agent.jsx'
import * as api from '../api.js'

vi.mock('../api.js')

describe('Agent', () => {
  it('renders a user message immediately and the assistant reply with trace chips', async () => {
    api.postChat.mockResolvedValueOnce({
      text: 'Three tasks are overdue in Marketing.',
      trace: [
        { tool: 'list_workspace', ok: true, ms: 50 },
        { tool: 'search_tasks', ok: true, ms: 120 },
      ],
      stopped_reason: 'complete',
    })

    const user = userEvent.setup()
    render(<Agent />)

    await user.type(screen.getByLabelText('Message'), "what's overdue in marketing?")
    await user.click(screen.getByRole('button', { name: /send/i }))

    expect(screen.getByText("what's overdue in marketing?")).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.getByText('Three tasks are overdue in Marketing.')).toBeInTheDocument()
    })
    expect(screen.getByText(/search_tasks/)).toBeInTheDocument()
    expect(screen.getByText(/list_workspace/)).toBeInTheDocument()
  })

  it('shows a pending state while the request is in flight', async () => {
    let resolveFn
    api.postChat.mockReturnValueOnce(
      new Promise((resolve) => {
        resolveFn = resolve
      }),
    )

    const user = userEvent.setup()
    render(<Agent />)

    await user.type(screen.getByLabelText('Message'), 'hello')
    await user.click(screen.getByRole('button', { name: /send/i }))

    expect(screen.getByText(/thinking/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /sending/i })).toBeDisabled()

    resolveFn({ text: 'hi!', trace: [], stopped_reason: 'complete' })
    await waitFor(() => expect(screen.getByText('hi!')).toBeInTheDocument())
  })

  it('surfaces the backend error message rather than a generic failure', async () => {
    api.postChat.mockRejectedValueOnce(new Error('ClickUp token invalid'))

    const user = userEvent.setup()
    render(<Agent />)

    await user.type(screen.getByLabelText('Message'), 'hello')
    await user.click(screen.getByRole('button', { name: /send/i }))

    await waitFor(() => {
      expect(screen.getByText('ClickUp token invalid')).toBeInTheDocument()
    })
  })
})
