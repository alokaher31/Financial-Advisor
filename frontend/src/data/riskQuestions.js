/**
 * Risk questionnaire question/answer IDs, mirrored verbatim from
 * backend/app/core/risk_scoring.py (RISK_QUESTIONNAIRE). That module is the
 * deterministic source of truth for scoring — calculate_risk_score()
 * requires every one of these question IDs to be present with one of the
 * listed answer IDs, or it raises. This file is READ-ONLY intent: if the
 * backend questionnaire changes, update this list to match rather than
 * inventing new questions here.
 *
 * The frontend never computes a score or category from these answers — it
 * only collects them and submits to POST /api/risk-assessment for the
 * backend to score.
 */
export const RISK_QUESTIONS = [
  {
    id: 'investment_experience',
    text: 'How much investment experience do you have?',
    options: [
      { id: 'none', label: 'None' },
      { id: 'basic', label: 'Very limited experience' },
      { id: 'some', label: 'Some experience' },
      { id: 'experienced', label: 'Several years of experience' },
      { id: 'extensive', label: 'Extensive experience' },
    ],
  },
  {
    id: 'market_drop_reaction',
    text: 'What would you most likely do if your portfolio fell by 20%?',
    options: [
      { id: 'sell_all', label: 'Sell all investments' },
      { id: 'sell_some', label: 'Sell part of the portfolio' },
      { id: 'hold', label: 'Hold and make no changes' },
      { id: 'wait_then_buy', label: 'Wait, then consider buying' },
      { id: 'buy_more', label: 'Invest more at lower prices' },
    ],
  },
  {
    id: 'income_stability',
    text: 'How stable is your regular income?',
    options: [
      { id: 'highly_unstable', label: 'Highly unstable' },
      { id: 'variable', label: 'Variable' },
      { id: 'mostly_stable', label: 'Mostly stable' },
      { id: 'stable', label: 'Stable' },
      { id: 'very_stable', label: 'Very stable' },
    ],
  },
  {
    id: 'investment_time_horizon',
    text: 'How long can you keep this money invested?',
    options: [
      { id: 'under_1_year', label: 'Less than 1 year' },
      { id: '1_to_3_years', label: '1 to 3 years' },
      { id: '3_to_5_years', label: '3 to 5 years' },
      { id: '5_to_10_years', label: '5 to 10 years' },
      { id: 'over_10_years', label: 'More than 10 years' },
    ],
  },
  {
    id: 'primary_goal',
    text: 'What is your primary objective for this investment?',
    options: [
      { id: 'capital_preservation', label: 'Preserve capital' },
      { id: 'income', label: 'Generate regular income' },
      { id: 'balanced', label: 'Balance income and growth' },
      { id: 'long_term_growth', label: 'Pursue long-term growth' },
      { id: 'aggressive_growth', label: 'Pursue aggressive growth' },
    ],
  },
  {
    id: 'volatility_comfort',
    text: 'How comfortable are you with changes in investment value?',
    options: [
      { id: 'none', label: 'Not comfortable' },
      { id: 'low', label: 'Comfortable with small changes' },
      { id: 'moderate', label: 'Comfortable with moderate changes' },
      { id: 'high', label: 'Comfortable with large changes' },
      { id: 'very_high', label: 'Comfortable with very large changes' },
    ],
  },
  {
    id: 'investment_knowledge',
    text: 'How would you describe your investment knowledge?',
    options: [
      { id: 'none', label: 'No knowledge' },
      { id: 'basic', label: 'Basic knowledge' },
      { id: 'intermediate', label: 'Intermediate knowledge' },
      { id: 'strong', label: 'Strong knowledge' },
      { id: 'advanced', label: 'Advanced knowledge' },
    ],
  },
  {
    id: 'emergency_fund_coverage',
    text: 'How many months of essential expenses could your emergency savings cover without selling investments?',
    options: [
      { id: 'under_1_month', label: 'Less than 1 month' },
      { id: '1_to_3_months', label: '1 to under 3 months' },
      { id: '3_to_6_months', label: '3 to under 6 months' },
      { id: '6_to_12_months', label: '6 to 12 months' },
      { id: 'over_12_months', label: 'More than 12 months' },
    ],
  },
  {
    id: 'debt_payment_pressure',
    text: 'How do your current debt payments affect your monthly finances?',
    options: [
      { id: 'severe', label: 'Payments make essential expenses difficult to meet' },
      { id: 'high', label: 'Payments significantly limit saving and flexibility' },
      { id: 'manageable', label: 'Payments are manageable with limited flexibility' },
      { id: 'low', label: 'Payments are comfortably manageable' },
      { id: 'none_or_minimal', label: 'I have no debt payments or only minimal payments' },
    ],
  },
  {
    id: 'loss_capacity',
    text: 'If this investment lost 20% and took several years to recover, how would that affect your essential expenses and financial goals?',
    options: [
      { id: 'major_disruption', label: 'It would prevent me from meeting essential commitments' },
      { id: 'significant_adjustments', label: 'It would require significant financial adjustments' },
      { id: 'some_adjustments', label: 'It would require some non-essential adjustments' },
      { id: 'minor_impact', label: 'It would have only a minor effect on my plans' },
      { id: 'no_material_impact', label: 'It would not materially affect essential expenses or goals' },
    ],
  },
]
