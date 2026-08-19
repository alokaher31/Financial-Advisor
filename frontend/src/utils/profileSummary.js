function numberOrZero(value) {
  const number = Number(value)
  return Number.isFinite(number) ? number : 0
}

function sumValues(values) {
  if (!values || typeof values !== 'object') return 0
  return Object.values(values).reduce((total, value) => total + numberOrZero(value), 0)
}

/** Calculate the Profile screen's live preview using the same basic formulas as the backend. */
export function calculateLiveProfileSummary(form) {
  const totalAssets = sumValues(form?.assets)
  const totalLiabilities = sumValues(form?.liabilities)
  const monthlyIncome = numberOrZero(form?.monthly_income)
  const monthlyExpenses = numberOrZero(form?.monthly_expenses)
  const monthlySurplus = monthlyIncome - monthlyExpenses

  return {
    totalAssets,
    totalLiabilities,
    netWorth: totalAssets - totalLiabilities,
    monthlySurplus,
    savingsRate: monthlyIncome === 0 ? 0 : monthlySurplus / monthlyIncome,
  }
}

export function hasFinancialValues(form) {
  if (!form) return false
  return [
    form.monthly_income,
    form.monthly_expenses,
    ...Object.values(form.assets || {}),
    ...Object.values(form.liabilities || {}),
  ].some((value) => value !== '' && value !== null && value !== undefined)
}
