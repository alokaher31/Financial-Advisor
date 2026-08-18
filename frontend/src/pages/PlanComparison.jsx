import { useState } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { comparePlans, selectPlan } from '../api/apiClient.js'
import { useAsyncAction } from '../hooks/useAsyncAction.js'
import PlanCard from '../components/PlanCard.jsx'
import DisclaimerBanner from '../components/DisclaimerBanner.jsx'
import ErrorState from '../components/ErrorState.jsx'
import EmptyState from '../components/EmptyState.jsx'

export default function PlanComparison() {
  const { state, dispatch } = useApp()
  const { run: runCompare, loading: comparing, error: compareError } = useAsyncAction(comparePlans)
  const { run: runSelect, loading: selecting, error: selectError } = useAsyncAction(selectPlan)
  const [selectingPlanName, setSelectingPlanName] = useState(null)

  const plans = state.plans

  if (!plans || plans.length === 0) {
    return (
      <EmptyState
        title="No plans available yet"
        description="Generate plans from the Goal step first."
        action={
          <button type="button" className="btn btn-primary" onClick={() => dispatch({ type: 'GO_TO_STEP', step: 'goal' })}>
            Go to Goal Input
          </button>
        }
      />
    )
  }

  async function handleCompare() {
    const comparison = await runCompare({
      profileId: state.profile.result?.profileId,
      goalId: state.goal.result?.goalId,
      plans,
    })
    if (comparison) dispatch({ type: 'SET_COMPARISON', comparison })
  }

  async function handleSelect(plan) {
    setSelectingPlanName(plan.planName)
    const result = await runSelect({ planId: plan.planId, profileId: state.profile.result?.profileId, planName: plan.planName })
    setSelectingPlanName(null)
    if (!result) return
    dispatch({ type: 'SET_SELECTED_PLAN', plan })
    dispatch({ type: 'COMPLETE_STEP', step: 'plans' })
  }

  function handleViewDetails(plan) {
    dispatch({ type: 'SET_VIEWING_PLAN', planName: plan.planName })
    dispatch({ type: 'GO_TO_STEP', step: 'planDetail' })
  }

  return (
    <div>
      <div className="page-header">
        <h1>Compare Your Plans</h1>
        <p>Three plans generated from your profile, risk assessment, and goal. All figures come from the planning engine.</p>
      </div>

      <DisclaimerBanner />

      <div className="plan-grid mt-4">
        {plans.map((plan) => (
          <PlanCard
            key={plan.planName}
            plan={plan}
            isSelected={state.selectedPlan?.planName === plan.planName}
            selecting={selecting && selectingPlanName === plan.planName}
            onSelect={handleSelect}
            onViewDetails={handleViewDetails}
          />
        ))}
      </div>

      {selectError && <ErrorState title="Couldn't select this plan" error={selectError} />}

      <div className="card mt-5">
        <div className="flex-between">
          <div>
            <h3>Side-by-Side Comparison</h3>
            <p className="text-muted mt-1">Get an AI-generated summary of how these plans stack up.</p>
          </div>
          <button type="button" className="btn btn-secondary" onClick={handleCompare} disabled={comparing}>
            {comparing ? (
              <>
                <span className="spinner spinner-sm" aria-hidden="true" /> Comparing...
              </>
            ) : (
              'Compare Plans'
            )}
          </button>
        </div>

        {compareError && <ErrorState title="Couldn't compare plans" error={compareError} onRetry={handleCompare} />}

        {state.comparison?.summary && (
          <div className="plan-card__ai-note mt-4">
            <strong>AI comparison:</strong> {state.comparison.summary}
          </div>
        )}
      </div>

      {state.selectedPlan && (
        <div className="page-actions page-actions--end">
          <button type="button" className="btn btn-primary" onClick={() => dispatch({ type: 'GO_TO_STEP', step: 'chatbot' })}>
            Continue with {state.selectedPlan.planName} Plan
          </button>
        </div>
      )}
    </div>
  )
}
