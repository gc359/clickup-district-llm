import { afterEach, describe, expect, it, vi } from 'vitest'
import { newSessionId } from './sessionId.js'

const UUID_V4 = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/

// captured before any stubbing, so the fallback test doesn't recurse into its own stub
const realCrypto = globalThis.crypto

afterEach(() => {
  vi.unstubAllGlobals()
})

describe('newSessionId', () => {
  it('uses crypto.randomUUID when available', () => {
    expect(newSessionId()).toMatch(UUID_V4)
  })

  it('falls back to getRandomValues in a non-secure context', () => {
    // http:// origins expose crypto.getRandomValues but not crypto.randomUUID
    vi.stubGlobal('crypto', {
      getRandomValues: (arr) => realCrypto.getRandomValues(arr),
    })

    expect(newSessionId()).toMatch(UUID_V4)
  })

  it('returns a distinct value on each call', () => {
    expect(newSessionId()).not.toBe(newSessionId())
  })
})
