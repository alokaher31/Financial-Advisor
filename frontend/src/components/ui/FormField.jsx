/**
 * Reusable labeled form control: label + input/select + hint + validation
 * error. Keeps form pages (ProfileForm, GoalInput, RiskQuestionnaire) free
 * of repeated label/error markup.
 */
export default function FormField({
  id,
  label,
  error,
  hint,
  prefix,
  required,
  children,
}) {
  return (
    <div className="form-field">
      <label htmlFor={id}>
        {label}
        {required && <span aria-hidden="true" style={{ color: 'var(--color-error)' }}> *</span>}
      </label>
      {prefix ? (
        <div className="input-prefix-group">
          <span className="input-prefix-group__prefix" aria-hidden="true">
            {prefix}
          </span>
          {children}
        </div>
      ) : (
        children
      )}
      {error ? (
        <span className="field-error" role="alert">
          {error}
        </span>
      ) : hint ? (
        <span className="field-hint">{hint}</span>
      ) : null}
    </div>
  )
}
