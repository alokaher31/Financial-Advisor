import { useState } from 'react'
import { useApp } from '../context/AppContext.jsx'
import { createProfile } from '../api/apiClient.js'
import { useAsyncAction } from '../hooks/useAsyncAction.js'
import FormField from '../components/ui/FormField.jsx'
import ErrorState from '../components/ErrorState.jsx'
import DisclaimerBanner from '../components/DisclaimerBanner.jsx'
import { formatCurrency, formatPercent } from '../utils/format.js'
import { validateRequiredNumber, validateOptionalNonNegativeNumber, hasErrors } from '../utils/validation.js'

const ASSET_FIELDS = [
  { key: 'equity', label: 'Equity / Investments' },
  { key: 'debt', label: 'Debt / Bonds' },
  { key: 'gold', label: 'Gold' },
  { key: 'real_estate', label: 'Real Estate' },
  { key: 'cash', label: 'Cash / FD' },
]

const LIABILITY_FIELDS = [
  { key: 'home_loan', label: 'Home Loan' },
  { key: 'personal_loan', label: 'Personal Loan' },
  { key: 'other_loans', label: 'Other Loans' },
]

function initialFormState(saved) {
  return {
    name: saved?.name ?? '',
    occupation: saved?.occupation ?? '',
    age: saved?.age ?? '',
    monthly_income: saved?.monthly_income ?? '',
    monthly_expenses: saved?.monthly_expenses ?? '',
    assets: {
      equity: saved?.assets?.equity ?? '',
      debt: saved?.assets?.debt ?? '',
      gold: saved?.assets?.gold ?? '',
      real_estate: saved?.assets?.real_estate ?? '',
      cash: saved?.assets?.cash ?? '',
    },
    liabilities: {
      home_loan: saved?.liabilities?.home_loan ?? '',
      personal_loan: saved?.liabilities?.personal_loan ?? '',
      other_loans: saved?.liabilities?.other_loans ?? '',
    },
  }
}

export default function ProfileForm() {
  const { state, dispatch } = useApp()
  const [form, setForm] = useState(() => initialFormState(state.profile.input))
  const [errors, setErrors] = useState({})
  const { run: submitProfile, loading, error } = useAsyncAction(createProfile)

  function updateField(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }))
  }

  function updateNested(group, key, value) {
    setForm((prev) => ({ ...prev, [group]: { ...prev[group], [key]: value } }))
  }

  function validate() {
    const nextErrors = {
      name: form.name.trim() ? null : 'Name is required',
      occupation: form.occupation.trim() ? null : 'Occupation is required',
      age: validateRequiredNumber(form.age, { min: 18, max: 100, label: 'Age' }),
      monthly_income: validateRequiredNumber(form.monthly_income, { min: 0, label: 'Monthly income' }),
      monthly_expenses: validateRequiredNumber(form.monthly_expenses, { min: 0, label: 'Monthly expenses' }),
    }
    for (const { key, label } of ASSET_FIELDS) {
      nextErrors[`assets.${key}`] = validateOptionalNonNegativeNumber(form.assets[key], { label })
    }
    for (const { key, label } of LIABILITY_FIELDS) {
      nextErrors[`liabilities.${key}`] = validateOptionalNonNegativeNumber(form.liabilities[key], { label })
    }
    setErrors(nextErrors)
    return !hasErrors(nextErrors)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!validate()) return

    const toNum = (v) => (v === '' ? 0 : Number(v))
    const payload = {
      name: form.name.trim(),
      occupation: form.occupation.trim(),
      age: toNum(form.age),
      monthly_income: toNum(form.monthly_income),
      monthly_expenses: toNum(form.monthly_expenses),
      assets: Object.fromEntries(ASSET_FIELDS.map(({ key }) => [key, toNum(form.assets[key])])),
      liabilities: Object.fromEntries(LIABILITY_FIELDS.map(({ key }) => [key, toNum(form.liabilities[key])])),
    }

    const result = await submitProfile(payload)
    if (!result) return
    dispatch({ type: 'SET_PROFILE', input: payload, result })
    dispatch({ type: 'COMPLETE_STEP', step: 'profile' })
    dispatch({ type: 'GO_TO_STEP', step: 'risk' })
  }

  const summary = state.profile.result

  return (
    <div>
      <div className="page-header">
        <h1>Your Financial Profile</h1>
        <p>Tell us about your income, expenses, and existing holdings so we can tailor a plan to your situation.</p>
      </div>

      <form onSubmit={handleSubmit} noValidate>
        <fieldset className="form-section">
          <legend>Basics</legend>
          <div className="form-grid">
            <FormField id="name" label="Full Name" required error={errors.name}>
              <input
                id="name"
                className={`input ${errors.name ? 'input--error' : ''}`}
                type="text"
                placeholder="e.g. Rajesh Kumar"
                value={form.name}
                onChange={(e) => updateField('name', e.target.value)}
              />
            </FormField>
            <FormField id="occupation" label="Occupation" required error={errors.occupation}>
              <input
                id="occupation"
                className={`input ${errors.occupation ? 'input--error' : ''}`}
                type="text"
                placeholder="e.g. Software Engineer"
                value={form.occupation}
                onChange={(e) => updateField('occupation', e.target.value)}
              />
            </FormField>
            <FormField id="age" label="Age" required error={errors.age}>
              <input
                id="age"
                className={`input ${errors.age ? 'input--error' : ''}`}
                type="number"
                min="18"
                max="100"
                value={form.age}
                onChange={(e) => updateField('age', e.target.value)}
              />
            </FormField>
            <FormField id="monthly_income" label="Monthly Income" required error={errors.monthly_income} prefix="₹">
              <input
                id="monthly_income"
                className={`input ${errors.monthly_income ? 'input--error' : ''}`}
                type="number"
                min="0"
                value={form.monthly_income}
                onChange={(e) => updateField('monthly_income', e.target.value)}
              />
            </FormField>
            <FormField id="monthly_expenses" label="Monthly Expenses" required error={errors.monthly_expenses} prefix="₹">
              <input
                id="monthly_expenses"
                className={`input ${errors.monthly_expenses ? 'input--error' : ''}`}
                type="number"
                min="0"
                value={form.monthly_expenses}
                onChange={(e) => updateField('monthly_expenses', e.target.value)}
              />
            </FormField>
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Assets</legend>
          <div className="form-grid">
            {ASSET_FIELDS.map(({ key, label }) => (
              <FormField key={key} id={`asset-${key}`} label={label} error={errors[`assets.${key}`]} prefix="₹">
                <input
                  id={`asset-${key}`}
                  className={`input ${errors[`assets.${key}`] ? 'input--error' : ''}`}
                  type="number"
                  min="0"
                  value={form.assets[key]}
                  onChange={(e) => updateNested('assets', key, e.target.value)}
                />
              </FormField>
            ))}
          </div>
        </fieldset>

        <fieldset className="form-section">
          <legend>Liabilities</legend>
          <div className="form-grid">
            {LIABILITY_FIELDS.map(({ key, label }) => (
              <FormField key={key} id={`liability-${key}`} label={label} error={errors[`liabilities.${key}`]} prefix="₹">
                <input
                  id={`liability-${key}`}
                  className={`input ${errors[`liabilities.${key}`] ? 'input--error' : ''}`}
                  type="number"
                  min="0"
                  value={form.liabilities[key]}
                  onChange={(e) => updateNested('liabilities', key, e.target.value)}
                />
              </FormField>
            ))}
          </div>
        </fieldset>

        {error && <ErrorState title="Couldn't save your profile" error={error} />}

        {summary && (
          <div className="card mt-4">
            <h3 className="mb-4">Financial Summary</h3>
            <div className="card-grid">
              <div className="stat-tile">
                <div className="stat-tile__label">Total Assets</div>
                <div className="stat-tile__value">{formatCurrency(summary.totalAssets)}</div>
              </div>
              <div className="stat-tile">
                <div className="stat-tile__label">Total Liabilities</div>
                <div className="stat-tile__value">{formatCurrency(summary.totalLiabilities)}</div>
              </div>
              <div className="stat-tile">
                <div className="stat-tile__label">Estimated Net Worth</div>
                <div
                  className={`stat-tile__value ${
                    typeof summary.netWorth === 'number'
                      ? summary.netWorth >= 0
                        ? 'stat-tile__value--positive'
                        : 'stat-tile__value--negative'
                      : ''
                  }`}
                >
                  {formatCurrency(summary.netWorth)}
                </div>
              </div>
              <div className="stat-tile">
                <div className="stat-tile__label">Monthly Surplus</div>
                <div className="stat-tile__value">{formatCurrency(summary.monthlySurplus)}</div>
                {typeof summary.savingsRate === 'number' && (
                  <div className="stat-tile__hint">{formatPercent(summary.savingsRate)} savings rate</div>
                )}
              </div>
            </div>
            <div className="mt-4">
              <DisclaimerBanner compact />
            </div>
          </div>
        )}

        <div className="page-actions page-actions--end">
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? (
              <>
                <span className="spinner spinner-sm" aria-hidden="true" /> Saving profile...
              </>
            ) : (
              'Continue to Risk Assessment'
            )}
          </button>
        </div>
      </form>
    </div>
  )
}
