function formatValidationItem(item) {
  if (typeof item === 'string') return item
  if (!item || typeof item !== 'object') return String(item ?? '')

  const message = item.msg || item.message || item.error
  if (message) {
    const location = Array.isArray(item.loc)
      ? item.loc.filter((part) => part !== 'body').join('.')
      : ''
    return location ? `${location}: ${message}` : String(message)
  }

  try {
    return JSON.stringify(item)
  } catch {
    return 'The server returned an invalid error response.'
  }
}

/** Convert API errors, including FastAPI validation arrays, into readable text. */
export function formatErrorMessage(error, fallback = 'Please check your connection and try again.') {
  if (!error) return fallback
  if (typeof error === 'string') return error

  if (Array.isArray(error)) {
    const messages = error.map(formatValidationItem).filter(Boolean)
    return messages.length ? messages.join('; ') : fallback
  }

  if (typeof error === 'object') {
    const nested = error.detail ?? error.message ?? error.error
    if (nested !== undefined && nested !== error) {
      return formatErrorMessage(nested, fallback)
    }
    return formatValidationItem(error) || fallback
  }

  return String(error)
}
