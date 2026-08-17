import AllocationChart from './AllocationChart.jsx'
import { RiskBadge } from './ui/Badge.jsx'
import { formatCurrency, formatPercent, formatSignedCurrency } from '../utils/format.js'

// Static UI copy only — not a financial calculation. Describes the plan
// style implied by its risk level; all numbers still come from props.
const DESCRIPTIONS = {
  Conservative: 'Prioritizes capital protection with lower expected volatility.',
  Moderate: 'Balances growth and stability across asset classes.',
  Aggressive: 'Leans into growth assets for higher long-term upside.',
}

/**
 * Presentational plan card. Renders only what it's given via props — it
 * does not calculate corpus, returns, or gaps itself. `plan` is expected to
 * be a normalized plan object from api/apiClient.js (see normalizePlan).
 */
export default function PlanCard({ plan, isSelected, onSelect, onViewDetails, selecting }) {
  const gap = plan.gapVsTarget
  const gapIsSurplus = typeof gap === 'number' && gap >= 0

  return (
    <div className={`card plan-card ${isSelected ? 'plan-card--selected' : ''}`}>
      {isSelected && <span className="selected-flag">Selected</span>}
      <div className="plan-card__header">
        <div>
          <div className="plan-card__title">{plan.planName}</div>
          <p className="plan-card__description">{DESCRIPTIONS[plan.riskLevel] || 'Personalized investment mix.'}</p>
        </div>
        <RiskBadge category={plan.riskLevel} />
      </div>

      <AllocationChart allocation={plan.allocation} size={130} strokeWidth={22} />

      <div className="plan-card__metrics">
        <div>
          <div className="plan-card__metric-label">Projected Corpus</div>
          <div className="plan-card__metric-value">{formatCurrency(plan.projectedCorpus)}</div>
        </div>
        <div>
          <div className="plan-card__metric-label">Monthly Investment</div>
          <div className="plan-card__metric-value">{formatCurrency(plan.requiredMonthlyInvestment)}</div>
        </div>
        <div>
          <div className="plan-card__metric-label">Gap vs Target</div>
          <div
            className="plan-card__metric-value"
            style={{ color: gapIsSurplus ? 'var(--color-success)' : 'var(--color-error)' }}
          >
            {formatSignedCurrency(gap)}
          </div>
        </div>
        <div>
          <div className="plan-card__metric-label">Expected Return</div>
          <div className="plan-card__metric-value">
            {typeof plan.blendedExpectedReturn === 'number'
              ? formatPercent(plan.blendedExpectedReturn, { alreadyPercent: true })
              : '—'}
          </div>
        </div>
      </div>

      {typeof plan.volatility === 'number' && (
        <p className="text-faint" style={{ fontSize: '0.78rem' }}>
          Illustrative volatility: {formatPercent(plan.volatility, { alreadyPercent: true })}
        </p>
      )}

      {plan.explanation && (
        <div className="plan-card__ai-note">
          <strong>AI insight:</strong> {plan.explanation}
        </div>
      )}

      <div className="page-actions" style={{ marginTop: 'auto' }}>
        {onViewDetails && (
          <button type="button" className="btn btn-secondary btn-block" onClick={() => onViewDetails(plan)}>
            View Details
          </button>
        )}
        {onSelect && (
          <button
            type="button"
            className="btn btn-primary btn-block"
            onClick={() => onSelect(plan)}
            disabled={selecting}
          >
            {selecting ? 'Selecting...' : isSelected ? 'Selected ✓' : 'Select This Plan'}
          </button>
        )}
      </div>
    </div>
  )
}
