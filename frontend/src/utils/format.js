/**
 * Presentation-only formatting helpers. These do not calculate financial
 * values — they only format numbers the backend already computed, which
 * net_worth_calculator.py's module docstring explicitly delegates to the
 * presentation layer ("Presentation layers are responsible for percentage
 * formatting.").
 */

const INR_FORMATTER = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
})

const NUMBER_FORMATTER = new Intl.NumberFormat('en-IN')

export function formatCurrency(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '—'
  return INR_FORMATTER.format(num)
}

export function formatIndianAmount(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '—'
  const absolute = Math.abs(num)
  const sign = num < 0 ? '-' : ''
  if (absolute >= 10_000_000) return `${sign}₹${(absolute / 10_000_000).toLocaleString('en-IN', { maximumFractionDigits: 2 })} crore`
  if (absolute >= 100_000) return `${sign}₹${(absolute / 100_000).toLocaleString('en-IN', { maximumFractionDigits: 2 })} lakh`
  return formatCurrency(num)
}

export function formatNumber(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '—'
  return NUMBER_FORMATTER.format(num)
}

/** `value` is a decimal ratio (0.25) unless `alreadyPercent` is true (25). */
export function formatPercent(value, { alreadyPercent = false, digits = 1 } = {}) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '—'
  const pct = alreadyPercent ? num : num * 100
  return `${pct.toFixed(digits)}%`
}

export function formatSignedCurrency(value) {
  const num = Number(value)
  if (!Number.isFinite(num)) return '—'
  const formatted = formatCurrency(Math.abs(num))
  return num < 0 ? `-${formatted}` : `+${formatted}`
}
