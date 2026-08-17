import { useApp } from '../context/AppContext.jsx'
import { selectPlan } from '../api/apiClient.js'
import { useAsyncAction } from '../hooks/useAsyncAction.js'
import AllocationChart from '../components/AllocationChart.jsx'
import { RiskBadge } from '../components/ui/Badge.jsx'
import DisclaimerBanner from '../components/DisclaimerBanner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'
import { formatCurrency, formatPercent, formatSignedCurrency } from '../utils/format.js'

export default function PlanDetail() {
  const { state, dispatch } = useApp()
  const { run: runSelect, loading: selecting, error: selectError } = useAsyncAction(selectPlan)

  const plan = state.plans.find((p) => p.planName === state.viewingPlanName)

  if (!plan) {
    return (
      <EmptyState
        title="Plan not found"
        description="Go back and choose a plan to view its details."
        action={
          <button type="button" className="btn btn-primary" onClick={() => dispatch({ type: 'GO_TO_STEP', step: 'plans' })}>
            Back to Plan Comparison
          </button>
        }
      />
    )
  }

  const isSelected = state.selectedPlan?.planName === plan.planName
  const gapIsSurplus = typeof plan.gapVsTarget === 'number' && plan.gapVsTarget >= 0

  async function handleSelect() {
    const result = await runSelect({ profileId: state.profile.result?.profileId, planName: plan.planName })
    if (!result) return
    dispatch({ type: 'SET_SELECTED_PLAN', plan })
    dispatch({ type: 'COMPLETE_STEP', step: 'plans' })
  }

  function handleAskAi() {
    dispatch({
      type: 'SET_CHAT_DRAFT',
      draft: `Tell me more about the ${plan.planName} plan.`,
    })
    dispatch({ type: 'GO_TO_STEP', step: 'chatbot' })
  }

  return (
    <div>
      <button type="button" className="btn btn-ghost btn-sm" onClick={() => dispatch({ type: 'GO_TO_STEP', step: 'plans' })}>
        ← Back to Plan Comparison
      </button>

      <div className="page-header mt-3">
        <div className="flex-row">
          <h1>{plan.planName} Plan</h1>
          <RiskBadge category={plan.riskLevel} />
          {isSelected && <span className="badge badge-info">Currently Selected</span>}
        </div>
      </div>

      <DisclaimerBanner />

      <div className="card mt-4">
        <div className="flex-row" style={{ alignItems: 'flex-start', flexWrap: 'wrap', gap: 'var(--space-6)' }}>
          <AllocationChart allocation={plan.allocation} size={190} strokeWidth={30} />

          <div className="card-grid" style={{ flex: 1, minWidth: 260 }}>
            <div className="stat-tile">
              <div className="stat-tile__label">Projected Corpus</div>
              <div className="stat-tile__value">{formatCurrency(plan.projectedCorpus)}</div>
            </div>
            <div className="stat-tile">
              <div className="stat-tile__label">Target Amount</div>
              <div className="stat-tile__value">{formatCurrency(state.goal.input?.target_amount)}</div>
            </div>
            <div className="stat-tile">
              <div className="stat-tile__label">Gap vs Target</div>
              <div
                className="stat-tile__value"
                style={{ color: gapIsSurplus ? 'var(--color-success)' : 'var(--color-error)' }}
              >
                {formatSignedCurrency(plan.gapVsTarget)}
              </div>
            </div>
            <div className="stat-tile">
              <div className="stat-tile__label">Required Monthly Investment</div>
              <div className="stat-tile__value">{formatCurrency(plan.requiredMonthlyInvestment)}</div>
            </div>
          </div>
        </div>
      </div>

      {plan.explanation && (
        <div className="card mt-4">
          <h3 className="mb-4">Why This Plan</h3>
          <div className="plan-card__ai-note">
            <strong>AI explanation:</strong> {plan.explanation}
          </div>
        </div>
      )}

      <div className="card mt-4">
        <h3 className="mb-4">Key Assumptions</h3>
        <ul style={{ margin: 0, paddingLeft: 'var(--space-5)', color: 'var(--color-text-muted)' }}>
          <li>
            Blended expected annual return:{' '}
            {typeof plan.blendedExpectedReturn === 'number'
              ? formatPercent(plan.blendedExpectedReturn, { alreadyPercent: true })
              : '—'}
          </li>
          {typeof plan.volatility === 'number' && (
            <li>Illustrative volatility: {formatPercent(plan.volatility, { alreadyPercent: true })}</li>
          )}
          <li>Time horizon: {state.goal.input?.time_horizon_years ?? '—'} year(s)</li>
          <li>Contributions assumed monthly, based on projected surplus and required investment.</li>
          <li>Returns are based on historical/assumed asset-class averages, not guaranteed future performance.</li>
        </ul>
      </div>

      {selectError && <ErrorState title="Couldn't select this plan" error={selectError} />}

      <div className="page-actions page-actions--between">
        <button type="button" className="btn btn-secondary" onClick={handleAskAi}>
          Ask AI About This Plan
        </button>
        <button type="button" className="btn btn-primary" onClick={handleSelect} disabled={selecting}>
          {selecting ? 'Selecting...' : isSelected ? 'Selected ✓' : 'Select This Plan'}
        </button>
      </div>
    </div>
  )
}
