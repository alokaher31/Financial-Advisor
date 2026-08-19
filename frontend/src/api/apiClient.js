/**
 * Centralized backend client. Every network call in this app goes through a
 * function exported here — pages/components never call fetch() directly.
 *
 * CONTRACT NOTE: This file is the ONLY integration seam between frontend and
 * backend. It maps frontend field names to backend expectations and normalises
 * backend responses into the shapes the UI components expect.
 *
 * Set VITE_USE_MOCK_DATA=true in .env.local only when demo data is desired.
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
import { formatErrorMessage } from '../utils/errorMessage.js';

const VITE_ENV = import.meta.env ?? {};

const API_BASE_URL = (
  VITE_ENV.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

// Real calculations are the safe default. Mock mode must be explicitly enabled
// because mock responses do not reflect any values entered by the user.
const USE_MOCK_DATA =
  String(VITE_ENV.VITE_USE_MOCK_DATA ?? 'false').toLowerCase() ===
  'true';

// Warn if running on mock data
if (USE_MOCK_DATA) {
  console.warn(
    '⚠️ WARNING: Running on MOCK DATA. Backend is not connected.\n' +
    'Values entered in the forms will not affect mock plan projections.\n' +
    'Set VITE_USE_MOCK_DATA=false and run the backend at ' + API_BASE_URL
  );
}

export class ApiError extends Error {
  constructor(message, { status, details } = {}) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.details = details;
  }
}

async function request(path, { method = 'GET', body } = {}) {
  // Get token from localStorage
  const token =
    window.localStorage.getItem('finance_advisor_token') ||
    window.sessionStorage.getItem('finance_advisor_token');
  
  let response;
  try {
    const headers = {};
    
    if (body) {
      headers['Content-Type'] = 'application/json';
    }
    
    if (token && token !== 'demo_token') {
      headers['Authorization'] = `Bearer ${token}`;
    }
    
    response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
      method,
      headers: Object.keys(headers).length > 0 ? headers : undefined,
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
    // Handle 401 Unauthorized - token expired or invalid
    if (response.status === 401) {
      // Clear invalid token
      window.localStorage.removeItem('finance_advisor_token');
      window.localStorage.removeItem('finance_advisor_user');
      window.sessionStorage.removeItem('finance_advisor_token');
      window.sessionStorage.removeItem('finance_advisor_user');
      window.dispatchEvent(new Event('finance-advisor:unauthorized'));
      
      const message = 'Not authenticated. Please log in again.';
      throw new ApiError(message, { status: response.status, details: payload });
    }
    
    const message = formatErrorMessage(
      payload,
      `Request failed with status ${response.status}`,
    );
    throw new ApiError(message, { status: response.status, details: payload });
  }

  return payload;
}

function pick(source, key, fallback) {
  return source && source[key] !== undefined ? source[key] : fallback;
}

// --- Helpers ---------------------------------------------------------------

/** Sum all numeric values in an object (used for assets/liabilities). */
function sumValues(obj) {
  if (!obj || typeof obj !== 'object') return 0;
  return Object.values(obj).reduce((s, v) => s + (Number(v) || 0), 0);
}

/** Map frontend display goal-type to backend enum value. */
const GOAL_TYPE_MAP = {
  'Retirement': 'retirement',
  'Home Purchase': 'home_purchase',
  'Education': 'education',
  'Emergency Fund': 'emergency_fund',
  'Wealth Creation': 'investment',
  'Other': 'other',
};

/** Map frontend display priority to backend enum value. */
const PRIORITY_MAP = {
  'High': 'high',
  'Medium': 'medium',
  'Low': 'low',
};

// --- Normalizers ----------------------------------------------------------

function normalizeProfileResponse(data) {
  return {
    profileId: pick(data, 'id', pick(data, 'profile_id', null)),
    totalAssets: pick(data, 'total_assets', undefined),
    totalLiabilities: pick(data, 'total_liabilities', undefined),
    netWorth: pick(data, 'net_worth', undefined),
    monthlySurplus: pick(data, 'monthly_surplus', undefined),
    savingsRate:
      typeof data?.monthly_surplus === 'number' && typeof data?.monthly_income === 'number' && data.monthly_income > 0
        ? data.monthly_surplus / data.monthly_income
        : pick(data, 'savings_rate', undefined),
    debtToIncomeRatio: pick(data, 'debt_to_income_ratio', undefined),
    raw: data,
  };
}

function normalizeRiskResult(data) {
  return {
    riskScore: pick(data, 'risk_score', undefined),
    riskCategory: pick(data, 'risk_category', undefined),
    riskAssessmentId: pick(data, 'id', null),
    raw: data,
  };
}

function normalizeGoalResponse(data) {
  return {
    goalId: pick(data, 'id', pick(data, 'goal_id', null)),
    raw: data,
  };
}

function normalizePlan(plan) {
  return {
    planId: pick(plan, 'id', null),
    planName: pick(plan, 'plan_name', pick(plan, 'name', 'Plan')),
    riskLevel: pick(plan, 'risk_level', undefined),
    allocation: pick(plan, 'allocation', {}),
    blendedExpectedReturn: pick(plan, 'blended_expected_return', undefined),
    monthlyInvestment: pick(plan, 'monthly_investment', undefined),
    currentSavings: pick(plan, 'current_savings', undefined),
    futureValueOfCurrentSavings: pick(plan, 'future_value_of_current_savings', undefined),
    totalPlannedContributions: pick(plan, 'total_planned_contributions', undefined),
    totalRequiredContributions: pick(plan, 'total_required_contributions', undefined),
    isGoalAchievable: pick(plan, 'is_goal_achievable', undefined),
    projectedCorpus: pick(plan, 'projected_corpus', undefined),
    gapVsTarget: pick(plan, 'gap_vs_target', undefined),
    requiredMonthlyInvestment: pick(
      plan,
      'required_monthly_investment',
      undefined,
    ),
    additionalMonthlyInvestmentNeeded: pick(
      plan,
      'additional_monthly_investment_needed',
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
    conversationId: pick(data, 'session_id', pick(data, 'conversation_id', undefined)),
    reply: pick(data, 'message', pick(data, 'reply', undefined)),
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
 * POST /api/v1/profile
 * Maps frontend { age, monthly_income, monthly_expenses, savings, assets, liabilities, name, occupation }
 * to backend { name, age, occupation, monthly_income, monthly_expenses, total_assets, total_liabilities }
 */
export async function createProfile(profileInput) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeProfileResponse({
      ...MOCK_PROFILE_RESPONSE,
      ...profileInput,
    });
  }

  // Map frontend fields to backend expectations
  const backendPayload = {
    name: profileInput.name || 'Customer',
    age: profileInput.age,
    occupation: profileInput.occupation || 'Professional',
    monthly_income: profileInput.monthly_income,
    monthly_expenses: profileInput.monthly_expenses,
    total_assets: typeof profileInput.assets === 'object'
      ? sumValues(profileInput.assets)
      : (profileInput.total_assets || profileInput.assets || 0),
    total_liabilities: typeof profileInput.liabilities === 'object'
      ? sumValues(profileInput.liabilities)
      : (profileInput.total_liabilities || profileInput.liabilities || 0),
  };

  const data = await request('/profile', {
    method: 'POST',
    body: backendPayload,
  });
  return normalizeProfileResponse(data);
}

/** Update an existing profile while preserving its database identity. */
export async function updateProfile(profileId, profileInput) {
  if (!profileId) return createProfile(profileInput);
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeProfileResponse({
      ...MOCK_PROFILE_RESPONSE,
      ...profileInput,
      id: profileId,
    });
  }

  const backendPayload = {
    name: profileInput.name || 'Customer',
    age: profileInput.age,
    occupation: profileInput.occupation || 'Professional',
    monthly_income: profileInput.monthly_income,
    monthly_expenses: profileInput.monthly_expenses,
    total_assets: typeof profileInput.assets === 'object'
      ? sumValues(profileInput.assets)
      : (profileInput.total_assets || profileInput.assets || 0),
    total_liabilities: typeof profileInput.liabilities === 'object'
      ? sumValues(profileInput.liabilities)
      : (profileInput.total_liabilities || profileInput.liabilities || 0),
  };

  const data = await request(`/profile/${profileId}`, {
    method: 'PUT',
    body: backendPayload,
  });
  return normalizeProfileResponse(data);
}

/** Create on first submission and update when navigating back to Profile. */
export function saveProfile({ profileId, profileInput }) {
  return profileId
    ? updateProfile(profileId, profileInput)
    : createProfile(profileInput);
}

/**
 * POST /api/v1/risk
 * Maps: profile_id → customer_id, path /risk-assessment → /risk
 */
export async function submitRiskAssessment({ profileId, answers }) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeRiskResult(MOCK_RISK_RESULT);
  }
  const data = await request('/risk', {
    method: 'POST',
    body: {
      customer_id: profileId,
      answers,
    },
  });
  return normalizeRiskResult(data);
}

/**
 * POST /api/v1/goal
 * Maps: profile_id → customer_id, current_amount → current_savings,
 * goal_type/priority display → enum, adds goal_name
 */
export async function createGoal(goalInput) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeGoalResponse({ ...MOCK_GOAL_RESPONSE, ...goalInput });
  }

  const goalTypeEnum = GOAL_TYPE_MAP[goalInput.goal_type] || goalInput.goal_type?.toLowerCase() || 'other';
  const priorityEnum = PRIORITY_MAP[goalInput.priority] || goalInput.priority?.toLowerCase() || 'medium';

  const backendPayload = {
    customer_id: goalInput.profile_id,
    goal_type: goalTypeEnum,
    goal_name: `${goalInput.goal_type} Fund`,
    target_amount: goalInput.target_amount,
    current_savings: goalInput.current_amount ?? goalInput.current_savings ?? 0,
    time_horizon_years: goalInput.time_horizon_years,
    priority: priorityEnum,
  };

  const data = await request('/goal', { method: 'POST', body: backendPayload });
  return normalizeGoalResponse(data);
}

/** Update an existing goal rather than creating duplicates after navigation. */
export async function updateGoal(goalId, goalInput) {
  if (!goalId) return createGoal(goalInput);
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeGoalResponse({ ...MOCK_GOAL_RESPONSE, ...goalInput, id: goalId });
  }

  const goalTypeEnum = GOAL_TYPE_MAP[goalInput.goal_type] || goalInput.goal_type?.toLowerCase() || 'other';
  const priorityEnum = PRIORITY_MAP[goalInput.priority] || goalInput.priority?.toLowerCase() || 'medium';
  const data = await request(`/goal/${goalId}`, {
    method: 'PUT',
    body: {
      goal_type: goalTypeEnum,
      goal_name: `${goalInput.goal_type} Fund`,
      target_amount: goalInput.target_amount,
      current_savings: goalInput.current_amount ?? goalInput.current_savings ?? 0,
      time_horizon_years: goalInput.time_horizon_years,
      priority: priorityEnum,
    },
  });
  return normalizeGoalResponse(data);
}

/** Create on first submission and update when navigating back to Goal. */
export function saveGoal({ goalId, goalInput }) {
  return goalId ? updateGoal(goalId, goalInput) : createGoal(goalInput);
}

/**
 * POST /api/v1/plans/generate
 * Maps profile/goal/risk IDs and the user's planned monthly investment.
 */
export async function generatePlans({ profileId, goalId, riskAssessmentId, monthlyInvestment }) {
  if (USE_MOCK_DATA) {
    await mockDelay(900);
    return normalizePlansResponse(MOCK_PLANS);
  }

  const body = {
    customer_id: profileId,
    goal_ids: [goalId],
    custom_parameters: { monthly_investment: monthlyInvestment },
  };
  if (riskAssessmentId) {
    body.risk_assessment_id = riskAssessmentId;
  }

  const data = await request('/plans/generate', {
    method: 'POST',
    body,
  });
  return normalizePlansResponse(data);
}

/**
 * POST /api/v1/plans/compare
 * Maps: profileId → customer_id, sends plan_ids from stored plan objects
 */
export async function comparePlans({ profileId, plans }) {
  if (USE_MOCK_DATA) {
    await mockDelay(700);
    return normalizeComparisonResponse(MOCK_COMPARISON_SUMMARY);
  }

  // Extract plan IDs from the stored plan objects
  const planIds = (plans || []).map(p => p.planId).filter(Boolean);

  const data = await request('/plans/compare', {
    method: 'POST',
    body: {
      customer_id: profileId,
      plan_ids: planIds,
    },
  });
  return normalizeComparisonResponse(data);
}

/**
 * POST /api/v1/plans/{planId}/select
 * Uses real plan ID instead of plan name
 */
export async function selectPlan({ planId, planName }) {
  if (USE_MOCK_DATA) {
    await mockDelay(400);
    return { ...MOCK_SELECT_PLAN_RESPONSE, selected_plan_name: planName };
  }
  return request(`/plans/${planId}/select`, {
    method: 'POST',
  });
}

/**
 * POST /api/v1/chat
 * Maps: context.profileId → customer_id, conversationId → session_id
 */
export async function sendChatMessage({ message, conversationId, context }) {
  if (USE_MOCK_DATA) {
    await mockDelay(650);
    return normalizeChatResponse(MOCK_CHAT_REPLY);
  }
  const data = await request('/chat', {
    method: 'POST',
    body: {
      customer_id: context?.profileId,
      message,
      session_id: conversationId || undefined,
      include_context: true,
    },
  });
  return normalizeChatResponse(data);
}

/**
 * POST /api/v1/plans/whatif
 * Maps profileId, planId, and goalId to backend identifiers.
 */
export async function runWhatIf({ profileId, goalId, planId, scenario }) {
  if (USE_MOCK_DATA) {
    await mockDelay(800);
    return normalizeWhatIfResponse(MOCK_WHATIF_RESULT);
  }
  const data = await request('/plans/whatif', {
    method: 'POST',
    body: {
      customer_id: profileId,
      goal_id: goalId,
      plan_id: planId,
      scenario,
    },
  });
  return normalizeWhatIfResponse(data);
}

export const apiConfig = { API_BASE_URL, USE_MOCK_DATA };
