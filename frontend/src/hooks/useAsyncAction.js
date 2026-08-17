import { useCallback, useState } from 'react'

/**
 * Wraps an async apiClient call with loading/error state so pages don't
 * each reimplement the same try/catch/finally boilerplate.
 *
 * const { run, loading, error } = useAsyncAction(createProfile)
 * const result = await run(payload) // returns undefined if it threw
 */
export function useAsyncAction(actionFn) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const run = useCallback(
    async (...args) => {
      setLoading(true)
      setError(null)
      try {
        return await actionFn(...args)
      } catch (err) {
        setError(err)
        return undefined
      } finally {
        setLoading(false)
      }
    },
    [actionFn],
  )

  const reset = useCallback(() => setError(null), [])

  return { run, loading, error, reset }
}
