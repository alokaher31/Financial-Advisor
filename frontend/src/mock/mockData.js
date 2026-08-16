/**
 * Frontend-only mock responses, used when VITE_USE_MOCK_DATA=true (see
 * frontend/.env.example) or as a fallback when a specific endpoint call
 * fails during early integration. These values exist purely to demonstrate
 * the UI — they are NOT financial calculations performed by this app. Every
 * number here stands in for a value that, against the real backend, comes
 * from backend/app/core/*.py, and every explanation string stands in for
 * GenAI output. Keep this file isolated from real API logic (api/apiClient.js).
 */

export const MOCK_PROFILE_RESPONSE = {
  profile_id: 'mock-profile-1',
  age: 32,
  monthly_income: 120000,
  monthly_expenses: 65000,
  savings: 400000,
  assets: {
    equity: 300000,
    debt: 150000,
    gold: 80000,
    real_estate: 2000000,
    cash: 400000,
  },
  liabilities: {
    home_loan: 1500000,
    personal_loan: 100000,
    other_loans: 0,
  },
  total_assets: 2930000,
  total_liabilities: 1600000,
  net_worth: 1330000,
  monthly_surplus: 55000,
  savings_rate: 0.4583,
  debt_to_income_ratio: 13.33,
}

export const MOCK_RISK_RESULT = {
  risk_score: 68,
  risk_category: 'Moderate',
}

export const MOCK_GOAL_RESPONSE = {
  goal_id: 'mock-goal-1',
  goal_type: 'Retirement',
  target_amount: 30000000,
  current_amount: 400000,
  time_horizon_years: 25,
  priority: 'High',
}

export const MOCK_PLANS = [
  {
    plan_name: 'Conservative',
    risk_level: 'Conservative',
    allocation: { Equity: 20, Debt: 50, Gold: 15, Real_Estate: 10, Cash: 5 },
    blended_expected_return: 8.4,
    projected_corpus: 21500000,
    gap_vs_target: -8500000,
    required_monthly_investment: 42000,
    volatility: 6.1,
    explanation:
      'This plan favors debt and gold to limit downside, which suits a lower risk tolerance but is projected to fall short of your target — consider a longer horizon or higher contribution.',
  },
  {
    plan_name: 'Balanced',
    risk_level: 'Moderate',
    allocation: { Equity: 50, Debt: 25, Gold: 15, Real_Estate: 10, Cash: 0 },
    blended_expected_return: 10.9,
    projected_corpus: 28700000,
    gap_vs_target: -1300000,
    required_monthly_investment: 55000,
    volatility: 10.8,
    explanation:
      'A 50% equity allocation balances growth and stability, tracking close to your retirement target with moderate volatility along the way.',
  },
  {
    plan_name: 'Growth',
    risk_level: 'Aggressive',
    allocation: { Equity: 70, Debt: 10, Gold: 10, Real_Estate: 10, Cash: 0 },
    blended_expected_return: 12.6,
    projected_corpus: 33200000,
    gap_vs_target: 3200000,
    required_monthly_investment: 55000,
    volatility: 15.4,
    explanation:
      'The higher equity weighting is projected to exceed your target, but expect sharper short-term swings — suitable given your moderate-to-high volatility comfort.',
  },
]

export const MOCK_COMPARISON_SUMMARY = {
  summary:
    'The Balanced plan offers the closest match to your Moderate risk profile and retirement horizon, reaching within 5% of your target corpus. Growth reaches your goal with room to spare but carries roughly 40% more volatility than Balanced. Conservative protects capital best but likely requires either a longer horizon or a larger monthly contribution to close its gap.',
  plans: MOCK_PLANS,
}

export const MOCK_SELECT_PLAN_RESPONSE = {
  status: 'saved',
  selected_plan_name: 'Balanced',
}

export const MOCK_CHAT_REPLY = {
  conversation_id: 'mock-conversation-1',
  reply:
    "Your Balanced plan holds 15% gold mainly to dampen volatility — gold tends to move independently of equities, which smooths returns when markets fall. It's a deliberate trade-off: slightly lower expected growth in exchange for a steadier ride toward your goal.",
}

export const MOCK_WHATIF_RESULT = {
  before: { monthly_investment: 55000, projected_corpus: 28700000 },
  after: { monthly_investment: 60000, projected_corpus: 30950000 },
  change: { projected_corpus_delta: 2250000 },
  explanation:
    'Adding ₹5,000 per month compounds over your remaining 25-year horizon into roughly an extra ₹22.5 lakh at the Balanced plan\'s blended return — a modest monthly increase with an outsized long-term effect.',
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms))
}

/** Simulates network latency so loading states are visible in demos. */
export function mockDelay(ms = 500) {
  return delay(ms)
}
