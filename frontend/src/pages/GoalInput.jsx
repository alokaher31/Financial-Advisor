import { useMemo, useState } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { createGoal, generatePlans } from '../api/apiClient.js'
import FormField from '../components/ui/FormField.jsx'
import ErrorState from '../components/ErrorState.jsx'
import { formatCurrency } from '../utils/format.js'
import { validateRequiredNumber, hasErrors } from '../utils/validation.js'

const GOAL_TYPES = ['Retirement', 'Home Purchase', 'Education', 'Emergency Fund', 'Wealth Creation', 'Other']
const PRIORITIES = ['High', 'Medium', 'Low']

function initialFormState(saved) {
  return {
    goal_type: saved?.goal_type ?? GOAL_TYPES[0],
    target_amount: saved?.target_amount ?? '',
    current_amount: saved?.current_amount ?? '',
    time_horizon_years: saved?.time_horizon_years ?? '',
    priority: saved?.priority ?? PRIORITIES[1],
  }
}

export default function GoalInput() {
  const { state, dispatch } = useApp()
  const [form, setForm] = useState(() => initialFormState(state.goal.input))
  const [errors, setErrors] = useState({})
  const [phase, setPhase] = useState('idle') // idle | saving-goal | generating-plans
  const [submitError, setSubmitError] = useState(null)

  const loading = phase !== 'idle'

  function updateField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  function validate() {
    const nextErrors = {
      target_amount: validateRequiredNumber(form.target_amount, { min: 1, label: 'Target amount' }),
      current_amount: validateRequiredNumber(form.current_amount, { min: 0, label: 'Current savings toward goal' }),
      time_horizon_years: validateRequiredNumber(form.time_horizon_years, { min: 1, max: 60, label: 'Time horizon' }),
    }
    setErrors(nextErrors)
    return !hasErrors(nextErrors)
  }

  const summaryReady = useMemo(() => {
    return form.target_amount !== '' && form.current_amount !== '' && form.time_horizon_years !== ''
  }, [form.target_amount, form.current_amount, form.time_horizon_years])

  async function handleSubmit(e) {
    e.preventDefault()
    if (!validate()) return
    setSubmitError(null)

    const payload = {
      profile_id: state.profile.result?.profileId,
      goal_type: form.goal_type,
      target_amount: Number(form.target_amount),
      current_amount: Number(form.current_amount),
      time_horizon_years: Number(form.time_horizon_years),
      priority: form.priority,
    }

    try {
      setPhase('saving-goal')
      const goalResult = await createGoal(payload)
      dispatch({ type: 'SET_GOAL', input: payload, result: goalResult })

      setPhase('generating-plans')
      const plans = await generatePlans({
        profileId: state.profile.result?.profileId,
        goalId: goalResult.goalId,
        riskCategory: state.risk.result?.riskCategory,
      })
      dispatch({ type: 'SET_PLANS', plans })
      dispatch({ type: 'COMPLETE_STEP', step: 'goal' })
      dispatch({ type: 'GO_TO_STEP', step: 'plans' })
    } catch (err) {
      setSubmitError(err)
    } finally {
      setPhase('idle')
    }
  }

  return (
    <div>
      <div className="page-header">
        <h1>Set Your Financial Goal</h1>
        <p>Tell us what you&rsquo;re planning for so we can generate personalized plans.</p>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <fieldset className="form-section">
          <legend>Goal Details</legend>
          <div className="form-grid">
            <FormField id="goal_type" label="Goal Type" required>
              <select
                id="goal_type"
                className="select"
                value={form.goal_type}
                onChange={(e) => updateField('goal_type', e.target.value)}
              >
                {GOAL_TYPES.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField id="priority" label="Priority" required>
              <select
                id="priority"
                className="select"
                value={form.priority}
                onChange={(e) => updateField('priority', e.target.value)}
              >
                {PRIORITIES.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </FormField>
            <FormField id="target_amount" label="Target Amount" required error={errors.target_amount} prefix="₹">
              <input
                id="target_amount"
                className={`input ${errors.target_amount ? 'input--error' : ''}`}
                type="number"
                min="0"
                value={form.target_amount}
                onChange={(e) => updateField('target_amount', e.target.value)}
              />
            </FormField>
            <FormField
              id="current_amount"
              label="Current Savings Toward Goal"
              required
              error={errors.current_amount}
              prefix="₹"
            >
              <input
                id="current_amount"
                className={`input ${errors.current_amount ? 'input--error' : ''}`}
                type="number"
                min="0"
                value={form.current_amount}
                onChange={(e) => updateField('current_amount', e.target.value)}
              />
            </FormField>
            <FormField
              id="time_horizon_years"
              label="Time Horizon (years)"
              required
              error={errors.time_horizon_years}
            >
              <input
                id="time_horizon_years"
                className={`input ${errors.time_horizon_years ? 'input--error' : ''}`}
                type="number"
                min="1"
                max="60"
                value={form.time_horizon_years}
                onChange={(e) => updateField('time_horizon_years', e.target.value)}
              />
            </FormField>
          </div>
        </fieldset>

        {summaryReady && (
          <div className="card mt-4">
            <h3 className="mb-4">Goal Summary</h3>
            <p>
              <strong>{form.goal_type}</strong> — target of{' '}
              <strong>{formatCurrency(Number(form.target_amount))}</strong> in{' '}
              <strong>{form.time_horizon_years} year(s)</strong>, starting from{' '}
              <strong>{formatCurrency(Number(form.current_amount))}</strong> already saved. Priority:{' '}
              <strong>{form.priority}</strong>.
            </p>
          </div>
        )}

        {submitError && <ErrorState title="Couldn't generate your plans" error={submitError} />}

        <div className="page-actions page-actions--end">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {phase === 'saving-goal' && (
              <>
                <span className="spinner spinner-sm" aria-hidden="true" /> Saving goal...
              </>
            )}
            {phase === 'generating-plans' && (
              <>
                <span className="spinner spinner-sm" aria-hidden="true" /> Generating your personalized plans...
              </>
            )}
            {phase === 'idle' && 'Generate My Plans'}
          </button>
        </div>
      </form>
    </div>
  )
}
