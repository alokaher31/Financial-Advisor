/**
 * Centralized backend client. Every network call in this app goes through a
 * function exported here — pages/components never call fetch() directly.
 *
 * CONTRACT NOTE: As of this writing, backend/app/api/*.py and
 * backend/app/models/*.py are empty stub files, and docs/api_spec.md is
 * empty too, so there is no committed request/response schema yet for
 * POST /api/profile, /api/risk-assessment, /api/goal, /api/plans/generate,
 * /api/plans/compare, /api/plans/select, /api/chat, /api/whatif. The shapes
 * assumed below were reverse-engineered from the one part of the backend
 * that IS implemented — the deterministic core:
 *   - backend/app/core/net_worth_calculator.py (assets/liabilities/income/expenses -> net worth, surplus, DTI, savings rate)
 *   - backend/app/core/goal_calculator.py (target/current amount, horizon years, annual return -> projected corpus, required SIP, gap)
 *   - backend/app/core/risk_scoring.py (question/answer ID map -> risk_score 0-100, risk_category Conservative/Moderate/Aggressive)
 *   - backend/app/core/plan_generator.py (-> plan_name, risk_level, allocation, blended_expected_return, projected_corpus, gap_vs_target, required_monthly_investment)
 *
 * Every response is passed through a normalize* function before use, so if
 * the real routes ship with slightly different field names/casing, only
 * this file needs to change — not every page. Set VITE_USE_MOCK_DATA=false
 * once the real endpoints exist (see frontend/.env.example).
 */

import {
  MOCK_PROFILE_RESPONSE,
  MOCK_RISK_RESULT,
  MOCK_GOAL_RESPONSE,
  MOCK_PLANS,
  MOCK_COMPARISON_SUMMARY,
  MOCK_SELECT_PLAN_RESPONSE,
  MOCK_CHAT_REPLY,
  MOCK_WHATIF_RESULT,
  mockDelay,
} from '../mock/mockData.js';

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

// Default to mock mode unless explicitly disabled, so the app is usable
// standalone while backend/app/api/*.py routes are still empty stubs.
const USE_MOCK_DATA =
  String(import.meta.env.VITE_USE_MOCK_DATA ?? 'true').toLowerCase() !==
  'false';

export class ApiError extends Error {
  constructor(message, { status, details } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function request(path, { method = 'GET', body } = {}) {
  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api${path}`, {
      method,
      headers: body ? { 'Content-Type': 'application/json' } : undefined,
      body: body ? JSON.stringify(body) : undefined,
    });
  } catch (networkError) {
    throw new ApiError(
      `Unable to reach the backend at ${API_BASE_URL}. Is it running?`,
      { details: networkError },
    );
  }

  const isJson = response.headers
    .get('content-type')
    ?.includes('application/json');
  const payload = isJson ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    const message =
      (payload && (payload.message || payload.detail || payload.error)) ||
      `Request failed with status ${response.status}`;
    throw new ApiError(message, { status: response.status, details: payload });
  }

  return payload;
}

function pick(source, key, fallback) {
  return source && source[key] !== undefined ? source[key] : fallback;
}

// --- Normalizers ----------------------------------------------------------

function normalizeProfileResponse(data) {
  return {
    profileId: pick(data, 'profile_id', null),
    totalAssets: pick(data, 'total_assets', undefined),
    totalLiabilities: pick(data, 'total_liabilities', undefined),
    netWorth: pick(data, 'net_worth', undefined),
    monthlySurplus: pick(data, 'monthly_surplus', undefined),
    savingsRate: pick(data, 'savings_rate', undefined),
    debtToIncomeRatio: pick(data, 'debt_to_income_ratio', undefined),
    raw: data,
  };
}

function normalizeRiskResult(data) {
  return {
    riskScore: pick(data, 'risk_score', undefined),
    riskCategory: pick(data, 'risk_category', undefined),
    raw: data,
  };
}

function normalizeGoalResponse(data) {
  return {
    goalId: pick(data, 'goal_id', null),
    raw: data,
  };
}

function normalizePlan(plan) {
  return {
    planName: pick(plan, 'plan_name', pick(plan, 'name', 'Plan')),
    riskLevel: pick(plan, 'risk_level', undefined),
    allocation: pick(plan, 'allocation', {}),
    blendedExpectedReturn: pick(plan, 'blended_expected_return', undefined),
    projectedCorpus: pick(plan, 'projected_corpus', undefined),
    gapVsTarget: pick(plan, 'gap_vs_target', undefined),
    requiredMonthlyInvestment: pick(
      plan,
      'required_monthly_investment',
      undefined,
    ),
    volatility: pick(plan, 'volatility', undefined),
    explanation: pick(
      plan,
      'explanation',
      pick(plan, 'ai_explanation', undefined),
    ),
  };
}

function normalizePlansResponse(data) {
  const plans = Array.isArray(data) ? data : pick(data, 'plans', []);
  return plans.map(normalizePlan);
}

function normalizeComparisonResponse(data) {
  return {
    summary: pick(data, 'summary', pick(data, 'comparison_summary', undefined)),
    plans: normalizePlansResponse(pick(data, 'plans', [])),
    raw: data,
  };
}

function normalizeChatResponse(data) {
  return {
    conversationId: pick(data, 'conversation_id', undefined),
    reply: pick(data, 'reply', pick(data, 'message', undefined)),
    raw: data,
  };
}

function normalizeWhatIfResponse(data) {
  return {
    before: pick(data, 'before', {}),
    after: pick(data, 'after', {}),
    change: pick(data, 'change', {}),
    explanation: pick(data, 'explanation', undefined),
    raw: data,
  };
}

// --- Public API -------------------------------------------------------

/**
 * POST /api/profile
 * @param {object} profileInput { age, monthly_income, monthly_expenses, savings, assets, liabilities }
 */
export async function createProfile(profileInput) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeProfileResponse({
      ...MOCK_PROFILE_RESPONSE,
      ...profileInput,
    });
  }
  const data = await request('/profile', {
    method: 'POST',
    body: profileInput,
  });
  return normalizeProfileResponse(data);
}

/**
 * POST /api/risk-assessment
 * @param {object} params { profileId, answers: { [questionId]: answerId } } — answers must
 * use the exact IDs from src/data/riskQuestions.js (mirrored from risk_scoring.py).
 */
export async function submitRiskAssessment({ profileId, answers }) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeRiskResult(MOCK_RISK_RESULT);
  }
  const data = await request('/risk-assessment', {
    method: 'POST',
    body: { profile_id: profileId, answers },
  });
  return normalizeRiskResult(data);
}

/**
 * POST /api/goal
 * @param {object} goalInput { profile_id, goal_type, target_amount, current_amount, time_horizon_years, priority }
 */
export async function createGoal(goalInput) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeGoalResponse({ ...MOCK_GOAL_RESPONSE, ...goalInput });
  }
  const data = await request('/goal', { method: 'POST', body: goalInput });
  return normalizeGoalResponse(data);
}

/**
 * POST /api/plans/generate
 * @param {object} params { profileId, goalId, riskCategory }
 * @returns {Promise<Array>} three normalized plans (Conservative/Balanced/Growth)
 */
export async function generatePlans({ profileId, goalId, riskCategory }) {
  if (USE_MOCK_DATA) {
    await mockDelay(900);
    return normalizePlansResponse(MOCK_PLANS);
  }
  const data = await request('/plans/generate', {
    method: 'POST',
    body: {
      profile_id: profileId,
      goal_id: goalId,
      risk_category: riskCategory,
    },
  });
  return normalizePlansResponse(data);
}

/**
 * POST /api/plans/compare
 * @param {object} params { profileId, goalId, plans } — sends the already-generated
 * plans back so the backend/GenAI layer can narrate a comparison without recomputation.
 */
export async function comparePlans({ profileId, goalId, plans }) {
  if (USE_MOCK_DATA) {
    await mockDelay(700);
    return normalizeComparisonResponse(MOCK_COMPARISON_SUMMARY);
  }
  const data = await request('/plans/compare', {
    method: 'POST',
    body: { profile_id: profileId, goal_id: goalId, plans },
  });
  return normalizeComparisonResponse(data);
}

/**
 * POST /api/plans/select
 * @param {object} params { profileId, planName }
 */
export async function selectPlan({ profileId, planName }) {
  if (USE_MOCK_DATA) {
    await mockDelay(400);
    return { ...MOCK_SELECT_PLAN_RESPONSE, selected_plan_name: planName };
  }
  return request('/plans/select', {
    method: 'POST',
    body: { profile_id: profileId, plan_name: planName },
  });
}

/**
 * POST /api/chat
 * @param {object} params { message, conversationId, context } — context carries whatever
 * IDs (profileId/goalId/selectedPlan) the backend needs to ground its answer.
 */
export async function sendChatMessage({ message, conversationId, context }) {
  if (USE_MOCK_DATA) {
    await mockDelay(650);
    return normalizeChatResponse(MOCK_CHAT_REPLY);
  }
  const data = await request('/chat', {
    method: 'POST',
    body: { message, conversation_id: conversationId, context },
  });
  return normalizeChatResponse(data);
}

/**
 * POST /api/whatif
 * @param {object} params { profileId, goalId, planName, scenario } — `scenario` describes
 * the hypothetical change, e.g. { type: 'extra_monthly_investment', amount: 5000 }.
 * The backend recalculates deterministically; this function never computes the result.
 */
export async function runWhatIf({ profileId, goalId, planName, scenario }) {
  if (USE_MOCK_DATA) {
    await mockDelay(800);
    return normalizeWhatIfResponse(MOCK_WHATIF_RESULT);
  }
  const data = await request('/whatif', {
    method: 'POST',
    body: {
      profile_id: profileId,
      goal_id: goalId,
      plan_name: planName,
      scenario,
    },
  });
  return normalizeWhatIfResponse(data);
}

export const apiConfig = { API_BASE_URL, USE_MOCK_DATA };
