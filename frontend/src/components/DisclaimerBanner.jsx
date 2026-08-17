/**
 * Financial disclaimer shown wherever plan figures, projections, or AI
 * explanations appear. Wording mirrors docs/disclaimer.md's intent
 * (illustrative only, no guaranteed returns, not financial advice); that
 * doc is currently an empty placeholder in this repo, so the copy below is
 * a safe default — update it here if the docs owner publishes final wording,
 * rather than editing docs/disclaimer.md directly.
 */
export default function DisclaimerBanner({ compact = false }) {
  if (compact) {
    return (
      <p className="text-faint" style={{ fontSize: '0.75rem' }}>
        Illustrative only. Returns are not guaranteed. This application does not provide financial advice.
      </p>
    )
  }

  return (
    <div className="alert alert-warning" role="note">
      <span aria-hidden="true">⚠️</span>
      <div>
        <strong>Illustrative only.</strong> Projections use historical/assumed
        rates of return and are not guaranteed. This application does not
        provide personalized financial, tax, or legal advice — consult a
        licensed advisor before making decisions.
      </div>
    </div>
  )
}
