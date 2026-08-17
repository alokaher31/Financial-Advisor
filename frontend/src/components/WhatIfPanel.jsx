import { useState } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { runWhatIf } from '../api/apiClient.js'
import { useAsyncAction } from '../hooks/useAsyncAction.js'
import ErrorState from './ErrorState.jsx'
import DisclaimerBanner from './DisclaimerBanner.jsx'
import { formatCurrency } from '../utils/format.js'

/**
 * Collects a hypothetical scenario ("what if I invest ₹5,000 more per
 * month?") and renders the backend's deterministic recalculation. This
 * component never computes the before/after numbers itself — it only
 * displays whatever POST /api/whatif returns.
 */
export default function WhatIfPanel() {
  const { state } = useApp()
  const [extraAmount, setExtraAmount] = useState('5000')
  const { run, loading, error, reset } = useAsyncAction(runWhatIf)
  const [result, setResult] = useState(null)

  const selectedPlan = state.selectedPlan

  if (!selectedPlan) {
    return (
      <div className="alert alert-info">
        Select a plan on the Plan Comparison screen to try a What-If scenario against it.
      </div>
    )
  }

  async function handleRun(e) {
    e.preventDefault()
    reset()
    const amount = Number(extraAmount)
    if (!Number.isFinite(amount) || amount === 0) return

    const response = await run({
      profileId: state.profile.result?.profileId,
      goalId: state.goal.result?.goalId,
      planName: selectedPlan.planName,
      scenario: { type: 'extra_monthly_investment', amount },
    })
    if (response) setResult(response)
  }

  return (
    <div className="card mt-5">
      <h3>What-If: Adjust Your Monthly Investment</h3>
      <p className="text-muted mt-1">
        See how a change to your monthly contribution affects the {selectedPlan.planName} plan. The backend
        recalculates this deterministically — nothing here is estimated in the browser.
      </p>

      <form onSubmit={handleRun} className="flex-row mt-4" style={{ flexWrap: 'wrap' }}>
        <div className="input-prefix-group" style={{ maxWidth: 220 }}>
          <span className="input-prefix-group__prefix">₹</span>
          <input
            className="input"
            type="number"
            aria-label="Additional monthly investment amount"
            value={extraAmount}
            onChange={(e) => setExtraAmount(e.target.value)}
          />
        </div>
        <span className="text-muted">extra per month</span>
        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? (
            <>
              <span className="spinner spinner-sm" aria-hidden="true" /> Recalculating...
            </>
          ) : (
            'Run What-If'
          )}
        </button>
      </form>

      {error && <ErrorState title="Couldn't run this scenario" error={error} onRetry={handleRun} />}

      {result && (
        <>
          <div className="whatif-result">
            <div className="whatif-result__col">
              <div className="stat-tile__label">Before</div>
              <div className="stat-tile__value">{formatCurrency(result.before?.monthly_investment)}</div>
              <div className="text-faint" style={{ fontSize: '0.78rem' }}>
                / month · corpus {formatCurrency(result.before?.projected_corpus)}
              </div>
            </div>
            <div className="whatif-result__arrow" aria-hidden="true">
              →
            </div>
            <div className="whatif-result__col">
              <div className="stat-tile__label">After</div>
              <div className="stat-tile__value stat-tile__value--positive">
                {formatCurrency(result.after?.monthly_investment)}
              </div>
              <div className="text-faint" style={{ fontSize: '0.78rem' }}>
                / month · corpus {formatCurrency(result.after?.projected_corpus)}
              </div>
            </div>
          </div>

          {result.explanation && (
            <div className="plan-card__ai-note mt-4">
              <strong>AI explanation:</strong> {result.explanation}
            </div>
          )}

          <div className="mt-4">
            <DisclaimerBanner compact />
          </div>
        </>
      )}
    </div>
  )
}
