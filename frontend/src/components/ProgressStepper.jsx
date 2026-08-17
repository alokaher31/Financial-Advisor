/**
 * Top-level journey indicator: Profile -> Risk -> Goal -> Plans -> Chat.
 * `steps` is [{ key, label }], `currentKey` is the active step's key, and
 * `completedKeys` marks steps the user has already finished so they can
 * jump backward.
 */
export default function ProgressStepper({ steps, currentKey, completedKeys = [], onStepClick }) {
  return (
    <nav className="stepper" aria-label="Financial planning progress">
      {steps.map((step, index) => {
        const isComplete = completedKeys.includes(step.key)
        const isActive = step.key === currentKey
        const isClickable = Boolean(onStepClick) && (isComplete || isActive)
        const stateClass = isComplete
          ? 'stepper__step--complete'
          : isActive
            ? 'stepper__step--active'
            : ''

        return (
          <span key={step.key} style={{ display: 'contents' }}>
            <span
              className={`stepper__step ${stateClass}`}
              role={isClickable ? 'button' : undefined}
              tabIndex={isClickable ? 0 : undefined}
              onClick={isClickable ? () => onStepClick(step.key) : undefined}
              onKeyDown={
                isClickable
                  ? (e) => {
                      if (e.key === 'Enter' || e.key === ' ') onStepClick(step.key)
                    }
                  : undefined
              }
              style={isClickable ? { cursor: 'pointer' } : undefined}
              aria-current={isActive ? 'step' : undefined}
            >
              <span className="stepper__circle">{isComplete ? '✓' : index + 1}</span>
              <span className="stepper__label">{step.label}</span>
            </span>
            {index < steps.length - 1 && <span className="stepper__connector" aria-hidden="true" />}
          </span>
        )
      })}
    </nav>
  )
}
