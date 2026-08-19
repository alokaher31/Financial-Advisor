import { formatErrorMessage } from '../utils/errorMessage.js'

/**
 * Standard failure state for any API-driven view, with an optional retry
 * action. `error` may be an Error instance, a string, or null/undefined.
 */
export default function ErrorState({
  title = 'Something went wrong',
  error,
  onRetry,
}) {
  const message = formatErrorMessage(error)

  return (
    <div className="alert alert-error" role="alert">
      <div style={{ flex: 1 }}>
        <strong>{title}</strong>
        <p className="mt-1" style={{ margin: 0 }}>
          {message}
        </p>
      </div>
      {onRetry && (
        <button type="button" className="btn btn-secondary btn-sm" onClick={onRetry}>
          Try again
        </button>
      )}
    </div>
  )
}
