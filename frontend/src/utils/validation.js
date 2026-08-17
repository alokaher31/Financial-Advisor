/**
 * Basic client-side UX validation only (required fields, numeric ranges).
 * This never performs financial calculations — it just stops obviously
 * bad input (blank, negative, non-numeric) from being submitted.
 */

export function parseNumber(rawValue) {
  if (rawValue === '' || rawValue === null || rawValue === undefined) return undefined
  const num = Number(rawValue)
  return Number.isFinite(num) ? num : NaN
}

export function validateRequiredNumber(rawValue, { min, max, label }) {
  const num = parseNumber(rawValue)
  if (num === undefined) return `${label} is required.`
  if (Number.isNaN(num)) return `${label} must be a valid number.`
  if (min !== undefined && num < min) return `${label} must be at least ${min}.`
  if (max !== undefined && num > max) return `${label} must be at most ${max}.`
  return null
}

export function validateOptionalNonNegativeNumber(rawValue, { label }) {
  if (rawValue === '' || rawValue === null || rawValue === undefined) return null
  const num = Number(rawValue)
  if (Number.isNaN(num)) return `${label} must be a valid number.`
  if (num < 0) return `${label} cannot be negative.`
  return null
}

export function hasErrors(errors) {
  return Object.values(errors).some(Boolean)
}
