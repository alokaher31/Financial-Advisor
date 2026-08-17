# Financial Advisor Frontend ↔ Backend Integration Plan

## Background
The frontend (React/Vite) and backend (FastAPI/SQLAlchemy) are complete but not integrated. Frontend currently runs in mock mode. This plan details every change needed to wire them together with minimal modifications.

---

## Proposed Changes

### 1. Environment — `frontend/.env.local` [NEW]

```
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
```

---

### 2. API Client — `frontend/src/api/apiClient.js` [MODIFY]

#### 2a. Fix API path prefix
Change request function from `/api${path}` → `/api/v1${path}`.

#### 2b. Profile — field mapping
Frontend sends `{ age, monthly_income, monthly_expenses, savings, assets: {...}, liabilities: {...} }`.
Backend requires `{ name, age, occupation, monthly_income, monthly_expenses, total_assets, total_liabilities }`.

In `createProfile()`:
- Sum `assets` object values → `total_assets`
- Sum `liabilities` object values → `total_liabilities`
- Pass `name` and `occupation` from input (added to ProfileForm below)
- Remove `savings`, nested `assets`, and nested `liabilities` from the backend payload
- In normalizer: map backend `id` → `profileId`, pass through calculated fields

#### 2c. Risk — field & path mapping
Frontend calls `/risk-assessment` with `{ profile_id, answers }`.
Backend expects `POST /risk/` with `{ customer_id, answers }`.

Changes:
- Path: `/risk-assessment` → `/risk/`
- Body: `profile_id` → `customer_id`
- Response normalizer: add `riskAssessmentId: pick(data, 'id', null)` to retain the real DB id

#### 2d. Goal — field mapping
Frontend sends `{ profile_id, goal_type: "Retirement", current_amount, target_amount, time_horizon_years, priority: "High" }`.
Backend expects `{ customer_id, goal_name, goal_type: "retirement", current_savings, target_amount, time_horizon_years, priority: "high" }`.

Changes in `createGoal()`:
- `profile_id` → `customer_id`
- `current_amount` → `current_savings`
- `goal_type` display → enum: `"Retirement"` → `"retirement"`, `"Home Purchase"` → `"home_purchase"`, `"Education"` → `"education"`, `"Emergency Fund"` → `"emergency_fund"`, `"Wealth Creation"` → `"investment"`, `"Other"` → `"other"`
- `priority` display → enum: `"High"` → `"high"`, `"Medium"` → `"medium"`, `"Low"` → `"low"`
- Add `goal_name` derived from `goal_type` display value (e.g., "Retirement Fund")
- Response normalizer: `id` → `goalId`

#### 2e. Plan generation — field mapping & persistence
Frontend sends `{ profile_id, goal_id, risk_category }`.
Backend expects `{ customer_id, goal_ids: [id], risk_assessment_id (optional) }`.

Changes in `generatePlans()`:
- `profile_id` → `customer_id`
- `goal_id` → `goal_ids: [goalId]`
- Send `risk_assessment_id` (stored from risk step) instead of `risk_category`
- **Critical**: backend `/generate` returns plain dicts (no DB ids). We need real plan IDs for `/select`.

**Solution — persist on generate**: Modify the backend `generate_financial_plans` route to persist each generated plan using the existing `crud.create_plan()` and `PlanCreate` model, then return plans with real `id` fields. This keeps changes inside the existing architecture (PlanDB, PlanCreate, crud.create_plan already exist).

Frontend normalizer: add `planId: pick(plan, 'id', null)` to `normalizePlan()`.

#### 2f. Plan selection — use real plan ID
Frontend currently sends `{ profile_id, plan_name }` to `POST /plans/select`.
Backend expects `POST /plans/{plan_id}/select` (no body, just path param).

Changes in `selectPlan()`:
- Accept `{ planId }` instead of `{ profileId, planName }`
- Call `request(\`/plans/${planId}/select\`, { method: 'POST' })`

#### 2g. Plan comparison — [NEW BACKEND ENDPOINT]
Frontend sends `{ profile_id, goal_id, plans }`.
Backend needs `POST /plans/compare`.

**Backend implementation**: Add route that accepts `{ customer_id, plan_ids }` or the plans array, generates a comparison summary deterministically, and returns `{ summary, plans }`.

Frontend: send `plan_ids` (collected from the stored plan objects with real IDs). Return format matches existing normalizer.

#### 2h. What-If — [NEW BACKEND ENDPOINT]
Frontend sends `{ profile_id, goal_id, plan_name, scenario: { type, amount } }`.
Backend needs `POST /whatif`.

**Backend implementation**: Add route that:
1. Loads the plan's allocation and the goal data
2. Recalculates `projected_corpus` with `current_monthly_investment + scenario.amount` using existing `calculate_future_value`
3. Returns `{ before: {...}, after: {...}, change: {...}, explanation }` matching the frontend's normalizer

#### 2i. Chat — field mapping
Frontend sends `{ message, conversation_id, context: { profileId, goalId, selectedPlanName } }`.
Backend expects `{ customer_id, message, session_id, include_context, max_history_messages }`.

Changes in `sendChatMessage()`:
- Map `context.profileId` → `customer_id`
- Map `conversationId` → `session_id`
- Drop `context` object (not in backend schema)
- Response: map `session_id` → `conversationId`, `message` → `reply`

---

### 3. ProfileForm — `frontend/src/pages/ProfileForm.jsx` [MODIFY]

Add `name` and `occupation` fields to the "Basics" fieldset. Both are required by the backend.

- Add `name: saved?.name ?? ''` and `occupation: saved?.occupation ?? ''` to `initialFormState`
- Add validation for both
- Add two `<FormField>` elements in the "Basics" fieldset (before age)
- Include in payload sent to `createProfile()`
- Preserve all existing styling

---

### 4. AppContext — `frontend/src/context/AppContext.jsx` [MODIFY]

Minor: No structural changes needed. The `profile.result.profileId`, `risk.result.riskAssessmentId`, `goal.result.goalId`, and `plans[].planId` will flow naturally from the updated normalizers.

---

### 5. GoalInput — `frontend/src/pages/GoalInput.jsx` [MODIFY]

- Use `state.profile.result?.profileId` as `customer_id` (already does this)
- Pass `riskAssessmentId` from `state.risk.result?.riskAssessmentId` to `generatePlans`
- No other changes needed (field mapping happens in apiClient)

---

### 6. PlanComparison — `frontend/src/pages/PlanComparison.jsx` [MODIFY]

- `handleSelect`: pass `{ planId: plan.planId }` instead of `{ profileId, planName }`
- `handleCompare`: pass plan IDs from stored plans

---

### 7. PlanDetail — `frontend/src/pages/PlanDetail.jsx` [MODIFY]

- `handleSelect`: pass `{ planId: plan.planId }` instead of `{ profileId, planName }`

---

### 8. WhatIfPanel — `frontend/src/components/WhatIfPanel.jsx` [MODIFY]

- Pass `planId` instead of `planName` (or keep planName + goalId + customer_id, depending on backend endpoint design)

---

### 9. Backend — Plan Generation Persistence [MODIFY]
#### `backend/app/api/plan_routes.py`

Modify `generate_financial_plans` to persist each plan using `crud.create_plan()` before returning. Map generated plan dicts to `PlanCreate` schema (with `AssetAllocation`, `GoalAllocation`, `MonthlyBreakdown` populated from the generated data and customer/goal data).

Return the persisted plans (with real DB `id`).

---

### 10. Backend — Compare Endpoint [NEW]
#### `backend/app/api/plan_routes.py`

Add `POST /compare` route:
- Accepts `{ customer_id, plan_ids: list[int] }`
- Loads plans from DB
- Generates deterministic comparison summary
- Returns `{ summary, plans, key_differences }`

---

### 11. Backend — What-If Endpoint [NEW]
#### `backend/app/api/plan_routes.py`

Add `POST /whatif` route (or new file):
- Accepts `{ customer_id, goal_id, plan_id, scenario: { type, amount } }`
- Loads plan and goal from DB
- Uses existing `calculate_future_value` / `calculate_required_monthly_investment`
- Returns `{ before, after, change, explanation }`

---

### 12. Backend Tests [NEW/MODIFY]
#### `backend/tests/test_api_integration.py`

Add tests for:
- Compare endpoint (valid, invalid plan IDs, missing customer)
- What-If endpoint (valid, invalid scenario, invalid IDs)
- Plan persistence in generate flow
- Plan select with real persisted ID
- Chat request/response mapping

---

## Verification Plan

### Automated Tests
```bash
cd backend && python -m pytest tests/ -v
```

### Frontend Build/Lint
```bash
cd frontend && npm run lint && npm run build
```

### Manual E2E
Profile → Risk → Goal → Generate Plans → Compare → Select → Chat → What-If

---

## Open Questions

> [!IMPORTANT]
> **Plan persistence on generate**: The backend currently returns generated plans as plain dicts without persisting. The spec requires using `POST /plans/{plan_id}/select` with a real DB id. The smallest change is to persist all 3 generated plans in `generate_financial_plans` and return them with IDs. This adds 3 DB rows per generate call. Is this acceptable, or would you prefer a different approach?

> [!NOTE]
> **Chat**: Backend uses a placeholder response (`"[This is a placeholder – chatbot module will provide detailed responses]"`). The existing `genai/chatbot.py` file exists but is empty (0 bytes). The integration will preserve the current placeholder behavior and report this clearly in the final report.

> [!NOTE]
> **Compare endpoint**: No LLM is wired up, so comparison will be generated deterministically from plan data (metrics comparison). The summary will describe differences in allocation, return, gap, and risk level.
