const RISK_CLASS_BY_CATEGORY = {
  Conservative: 'badge-conservative',
  Moderate: 'badge-moderate',
  Aggressive: 'badge-aggressive',
}

/**
 * Renders a risk-category pill. `category` is expected to be one of the
 * values produced by backend/app/core/risk_scoring.py::classify_risk
 * ("Conservative" | "Moderate" | "Aggressive"). Unknown values fall back to
 * a neutral badge instead of throwing, since this may render before the
 * real backend contract is finalized.
 */
export function RiskBadge({ category }) {
  if (!category) return null
  const className = RISK_CLASS_BY_CATEGORY[category] || 'badge-neutral'
  return <span className={`badge ${className}`}>{category}</span>
}

export function Badge({ variant = 'neutral', children }) {
  return <span className={`badge badge-${variant}`}>{children}</span>
}
