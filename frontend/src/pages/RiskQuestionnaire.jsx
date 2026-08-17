import { useState } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { submitRiskAssessment } from '../api/apiClient.js'
import { useAsyncAction } from '../hooks/useAsyncAction.js'
import { RISK_QUESTIONS } from '../data/riskQuestions.js'
import { RiskBadge } from '../components/ui/Badge.jsx'
import ErrorState from '../components/ErrorState.jsx'

export default function RiskQuestionnaire() {
  const { state, dispatch } = useApp()
  const [answers, setAnswers] = useState(state.risk.answers || {})
  const [index, setIndex] = useState(0)
  const [touchedError, setTouchedError] = useState(false)
  const { run: submitAnswers, loading, error } = useAsyncAction(submitRiskAssessment)

  const result = state.risk.result
  const total = RISK_QUESTIONS.length
  const question = RISK_QUESTIONS[index]
  const isLast = index === total - 1
  const answeredCount = Object.keys(answers).length
  const progressPct = Math.round((answeredCount / total) * 100)

  function selectAnswer(optionId) {
    setAnswers((prev) => ({ ...prev, [question.id]: optionId }))
    setTouchedError(false)
  }

  function goNext() {
    if (!answers[question.id]) {
      setTouchedError(true)
      return
    }
    dispatch({ type: 'SET_RISK_ANSWERS', answers })
    if (isLast) {
      handleSubmit()
    } else {
      setIndex((i) => i + 1)
    }
  }

  function goBack() {
    if (index === 0) return
    setIndex((i) => i - 1)
  }

  async function handleSubmit() {
    const submitted = await submitAnswers({ profileId: state.profile.result?.profileId, answers })
    if (!submitted) return
    dispatch({ type: 'SET_RISK_RESULT', result: submitted })
    dispatch({ type: 'COMPLETE_STEP', step: 'risk' })
  }

  function proceedToGoal() {
    dispatch({ type: 'GO_TO_STEP', step: 'goal' })
  }

  function retakeQuestionnaire() {
    dispatch({ type: 'SET_RISK_RESULT', result: null })
    setIndex(0)
  }

  if (result) {
    return (
      <div>
        <div className="page-header">
          <h1>Risk Assessment Complete</h1>
          <p>This score comes from the backend&rsquo;s deterministic risk scoring engine.</p>
        </div>
        <div className="card">
          <div className="flex-between">
            <div>
              <div className="stat-tile__label">Risk Score</div>
              <div className="stat-tile__value" style={{ fontSize: '2rem' }}>
                {typeof result.riskScore === 'number' ? `${result.riskScore}/100` : '—'}
              </div>
            </div>
            <RiskBadge category={result.riskCategory} />
          </div>
          {typeof result.riskScore === 'number' && (
            <div className="progress-bar mt-4">
              <div className="progress-bar__fill" style={{ width: `${result.riskScore}%` }} />
            </div>
          )}
        </div>
        <div className="page-actions page-actions--between">
          <button type="button" className="btn btn-ghost" onClick={retakeQuestionnaire}>
            Retake Questionnaire
          </button>
          <button type="button" className="btn btn-primary" onClick={proceedToGoal}>
            Continue to Goal Input
          </button>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h1>Risk Assessment</h1>
        <p>Question {index + 1} of {total}. Your answers are scored by the backend — this app only collects them.</p>
      </div>

      <div className="progress-bar mb-4">
        <div className="progress-bar__fill" style={{ width: `${progressPct}%` }} />
      </div>

      <div className="card">
        <h3>{question.text}</h3>
        <div className="stack mt-4">
          {question.options.map((option) => {
            const selected = answers[question.id] === option.id
            return (
              <label
                key={option.id}
                className="card card--tight"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 'var(--space-3)',
                  cursor: 'pointer',
                  borderColor: selected ? 'var(--color-primary)' : undefined,
                  boxShadow: selected ? '0 0 0 3px var(--color-accent-soft)' : undefined,
                }}
              >
                <input
                  type="radio"
                  name={question.id}
                  value={option.id}
                  checked={selected}
                  onChange={() => selectAnswer(option.id)}
                />
                <span>{option.label}</span>
              </label>
            )
          })}
        </div>
        {touchedError && (
          <p className="field-error mt-3" role="alert">
            Please select an answer to continue.
          </p>
        )}
      </div>

      {error && <ErrorState title="Couldn't submit your risk assessment" error={error} onRetry={handleSubmit} />}

      <div className="page-actions page-actions--between">
        <button type="button" className="btn btn-secondary" onClick={goBack} disabled={index === 0 || loading}>
          Back
        </button>
        <button type="button" className="btn btn-primary" onClick={goNext} disabled={loading}>
          {loading ? (
            <>
              <span className="spinner spinner-sm" aria-hidden="true" /> Scoring...
            </>
          ) : isLast ? (
            'Submit Assessment'
          ) : (
            'Next'
          )}
        </button>
      </div>
    </div>
  )
}
