/**
 * Standard in-progress state for any API-driven view. Never leave a screen
 * blank while waiting on the backend.
 */
export default function LoadingState({ message = 'Loading...' }) {
  return (
    <div className="state-block" role="status" aria-live="polite">
      <div className="spinner" />
      <p>{message}</p>
    </div>
  )
}
