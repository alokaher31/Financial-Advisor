import test from 'node:test'
import assert from 'node:assert/strict'

import { saveGoal, saveProfile } from '../src/api/apiClient.js'
import { formatErrorMessage } from '../src/utils/errorMessage.js'
import { calculateLiveProfileSummary } from '../src/utils/profileSummary.js'

function storageStub() {
  return {
    getItem: () => null,
    removeItem: () => {},
  }
}

globalThis.window = {
  localStorage: storageStub(),
  sessionStorage: storageStub(),
  dispatchEvent: () => {},
}

function jsonResponse(body) {
  return new Response(JSON.stringify(body), {
    status: 200,
    headers: { 'content-type': 'application/json' },
  })
}

test('editing an existing profile sends PUT and preserves its ID', async () => {
  let captured
  globalThis.fetch = async (url, options) => {
    captured = { url, options }
    return jsonResponse({
      id: 42,
      name: 'Meera',
      age: 28,
      occupation: 'Engineer',
      monthly_income: 120000,
      monthly_expenses: 60000,
      total_assets: 500000,
      total_liabilities: 0,
      net_worth: 500000,
      monthly_surplus: 60000,
      debt_to_income_ratio: 0,
      created_at: '2026-01-01T00:00:00Z',
      updated_at: '2026-01-01T00:00:00Z',
    })
  }

  const result = await saveProfile({
    profileId: 42,
    profileInput: {
      name: 'Meera',
      age: 28,
      occupation: 'Engineer',
      monthly_income: 120000,
      monthly_expenses: 60000,
      assets: { equity: 500000 },
      liabilities: { home_loan: 0 },
    },
  })

  assert.equal(captured.url, 'http://localhost:8000/api/v1/profile/42')
  assert.equal(captured.options.method, 'PUT')
  assert.equal(JSON.parse(captured.options.body).monthly_income, 120000)
  assert.equal(result.profileId, 42)
})

test('editing an existing goal sends PUT instead of creating a duplicate', async () => {
  let captured
  globalThis.fetch = async (url, options) => {
    captured = { url, options }
    return jsonResponse({ id: 9 })
  }

  const result = await saveGoal({
    goalId: 9,
    goalInput: {
      profile_id: 42,
      goal_type: 'Retirement',
      target_amount: 30000000,
      current_amount: 500000,
      monthly_investment: 15000,
      time_horizon_years: 25,
      priority: 'High',
    },
  })

  assert.equal(captured.url, 'http://localhost:8000/api/v1/goal/9')
  assert.equal(captured.options.method, 'PUT')
  assert.equal(JSON.parse(captured.options.body).target_amount, 30000000)
  assert.equal(result.goalId, 9)
})

test('FastAPI validation arrays become readable messages', () => {
  const message = formatErrorMessage({
    detail: [
      { loc: ['body', 'monthly_income'], msg: 'Input should be greater than 0' },
      { loc: ['body', 'age'], msg: 'Input should be less than or equal to 100' },
    ],
  })

  assert.equal(
    message,
    'monthly_income: Input should be greater than 0; age: Input should be less than or equal to 100',
  )
  assert.doesNotMatch(message, /\[object Object\]/)
})

test('financial summary recalculates directly from edited form values', () => {
  const first = calculateLiveProfileSummary({
    monthly_income: '50000',
    monthly_expenses: '30000',
    assets: { equity: '100000', cash: '50000' },
    liabilities: { personal_loan: '25000' },
  })
  const edited = calculateLiveProfileSummary({
    monthly_income: '80000',
    monthly_expenses: '30000',
    assets: { equity: '200000', cash: '50000' },
    liabilities: { personal_loan: '25000' },
  })

  assert.deepEqual(first, {
    totalAssets: 150000,
    totalLiabilities: 25000,
    netWorth: 125000,
    monthlySurplus: 20000,
    savingsRate: 0.4,
  })
  assert.deepEqual(edited, {
    totalAssets: 250000,
    totalLiabilities: 25000,
    netWorth: 225000,
    monthlySurplus: 50000,
    savingsRate: 0.625,
  })
})
