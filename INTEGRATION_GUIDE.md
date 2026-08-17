# 🔗 Frontend-Backend Integration Guide

## 📋 Current Status Overview

### ✅ Backend (Complete)
- **API**: 30+ endpoints fully implemented
- **Database**: SQLAlchemy ORM with seed data
- **CORS**: Configured for `localhost:3000` and `localhost:5173`
- **Running on**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

### ✅ Frontend (Complete)
- **Framework**: React + Vite
- **API Client**: Centralized in `src/api/apiClient.js`
- **Mock Mode**: Currently using `VITE_USE_MOCK_DATA=true`
- **Running on**: `http://localhost:5173` (via Vite)

---

## 🎯 Integration Strategy

### **Phase 1: API Endpoint Mapping** ✅ VERIFIED
### **Phase 2: Update API Client** ⚠️ NEEDS ADJUSTMENT
### **Phase 3: Switch from Mock to Real** 🎬 READY TO GO
### **Phase 4: Test & Verify** 🧪 PENDING

---

## 📊 API Endpoint Mapping

### ✅ **Matches Found (No Changes Needed)**

| Frontend Function | Frontend Expects | Backend Provides | Status |
|------------------|------------------|------------------|---------|
| `createProfile()` | POST `/api/profile` | POST `/api/v1/profile` | ✅ CLOSE |
| `submitRiskAssessment()` | POST `/api/risk-assessment` | POST `/api/v1/risk` | ⚠️ PATH |
| `createGoal()` | POST `/api/goal` | POST `/api/v1/goal` | ✅ CLOSE |
| `generatePlans()` | POST `/api/plans/generate` | POST `/api/v1/plans/generate` | ✅ CLOSE |
| `comparePlans()` | POST `/api/plans/compare` | ⚠️ NOT IMPLEMENTED | ❌ MISSING |
| `selectPlan()` | POST `/api/plans/select` | POST `/api/v1/plans/{id}/select` | ⚠️ PATH |
| `sendChatMessage()` | POST `/api/chat` | POST `/api/v1/chat` | ✅ CLOSE |
| `runWhatIf()` | POST `/api/whatif` | ⚠️ NOT IMPLEMENTED | ❌ MISSING |

---

## 🔧 Required Changes

### **Issue 1: API Path Prefix**
**Problem**: Frontend expects `/api/*`, Backend provides `/api/v1/*`

**Solution Options**:

#### **Option A: Update Frontend API Client** (RECOMMENDED)
```javascript
// frontend/src/api/apiClient.js
const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
).replace(/\/+$/, '');

// Change this line:
// fetch(`${API_BASE_URL}/api${path}`)
// To:
fetch(`${API_BASE_URL}/api/v1${path}`)
```

#### **Option B: Update Backend Prefix**
```python
# backend/app/config.py
API_V1_PREFIX: str = "/api"  # Change from "/api/v1"
```

**Recommendation**: **Option A** - Keep backend as `/api/v1` (industry standard for versioning)

---

### **Issue 2: Request/Response Field Name Mismatches**

#### **Profile Endpoint**

**Frontend Sends**:
```javascript
{
  age, monthly_income, monthly_expenses, 
  savings, assets, liabilities
}
```

**Backend Expects** (`CustomerProfileCreate`):
```python
{
  name, age, occupation,
  monthly_income, monthly_expenses,
  total_assets, total_liabilities
}
```

**MISMATCH**:
- ❌ Frontend: `assets` → Backend: `total_assets`
- ❌ Frontend: `liabilities` → Backend: `total_liabilities`
- ❌ Frontend missing: `name`, `occupation`
- ❌ Backend doesn't use: `savings`

#### **Risk Assessment**

**Frontend Sends**:
```javascript
{
  profile_id: profileId,
  answers: { questionId: answerId }
}
```

**Backend Expects** (`RiskAssessmentCreate`):
```python
{
  customer_id: int,
  answers: { questionId: answerId }
}
```

**MISMATCH**:
- ❌ Frontend: `profile_id` → Backend: `customer_id`

#### **Generate Plans**

**Frontend Sends**:
```javascript
{
  profile_id, goal_id, risk_category
}
```

**Backend Expects** (`PlanCreateRequest`):
```python
{
  customer_id: int,
  goal_ids: [int],  // Array!
  risk_assessment_id: Optional[int]
}
```

**MISMATCH**:
- ❌ Frontend: `profile_id` → Backend: `customer_id`
- ❌ Frontend: `goal_id` (single) → Backend: `goal_ids` (array)
- ❌ Frontend: `risk_category` → Backend uses `risk_assessment_id`

---

### **Issue 3: Missing Backend Endpoints**

These frontend functions have **no backend implementation**:

1. ❌ `POST /api/plans/compare` - Plan comparison
2. ❌ `POST /api/whatif` - What-if scenario analysis

**Need to implement** or **disable in frontend**.

---

## 🛠️ Step-by-Step Integration Plan

### **Step 1: Update Environment Variables**

```bash
# frontend/.env.local (create this file)
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
```

### **Step 2: Fix API Client Path Prefix**

```javascript
// frontend/src/api/apiClient.js (line ~69)

// CHANGE THIS:
async function request(path, { method = 'GET', body } = {}) {
  response = await fetch(`${API_BASE_URL}/api${path}`, {

// TO THIS:
async function request(path, { method = 'GET', body } = {}) {
  response = await fetch(`${API_BASE_URL}/api/v1${path}`, {
```

### **Step 3: Fix Field Name Mappings**

#### **A. Create Profile Function**

```javascript
// frontend/src/api/apiClient.js

export async function createProfile(profileInput) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeProfileResponse({
      ...MOCK_PROFILE_RESPONSE,
      ...profileInput,
    });
  }
  
  // MAP FRONTEND FIELDS TO BACKEND FIELDS
  const backendPayload = {
    name: profileInput.name || "Customer",  // ADD
    age: profileInput.age,
    occupation: profileInput.occupation || "Professional",  // ADD
    monthly_income: profileInput.monthly_income,
    monthly_expenses: profileInput.monthly_expenses,
    total_assets: profileInput.assets || profileInput.total_assets,  // MAP
    total_liabilities: profileInput.liabilities || profileInput.total_liabilities,  // MAP
  };
  
  const data = await request('/profile', {
    method: 'POST',
    body: backendPayload,
  });
  
  // MAP BACKEND RESPONSE TO FRONTEND EXPECTED FORMAT
  return normalizeProfileResponse({
    profile_id: data.id,  // Backend returns 'id'
    total_assets: data.total_assets,
    total_liabilities: data.total_liabilities,
    net_worth: data.net_worth,
    monthly_surplus: data.monthly_surplus,
    savings_rate: (data.monthly_surplus / data.monthly_income) * 100,
    debt_to_income_ratio: data.debt_to_income_ratio,
  });
}
```

#### **B. Risk Assessment Function**

```javascript
export async function submitRiskAssessment({ profileId, answers }) {
  if (USE_MOCK_DATA) {
    await mockDelay();
    return normalizeRiskResult(MOCK_RISK_RESULT);
  }
  
  const data = await request('/risk', {  // CHANGED PATH
    method: 'POST',
    body: { 
      customer_id: profileId,  // CHANGED FROM profile_id
      answers 
    },
  });
  
  return normalizeRiskResult({
    risk_score: data.risk_score,
    risk_category: data.risk_category,
  });
}
```

#### **C. Generate Plans Function**

```javascript
export async function generatePlans({ profileId, goalId, riskCategory }) {
  if (USE_MOCK_DATA) {
    await mockDelay(900);
    return normalizePlansResponse(MOCK_PLANS);
  }
  
  // Backend expects different structure
  const data = await request('/plans/generate', {
    method: 'POST',
    body: {
      customer_id: profileId,  // CHANGED
      goal_ids: [goalId],  // CHANGED TO ARRAY
      // Backend uses risk_assessment_id, not risk_category
      // We'll need to fetch the latest risk assessment
    },
  });
  
  return normalizePlansResponse(data);
}
```

#### **D. Select Plan Function**

```javascript
export async function selectPlan({ profileId, planName }) {
  if (USE_MOCK_DATA) {
    await mockDelay(400);
    return { ...MOCK_SELECT_PLAN_RESPONSE, selected_plan_name: planName };
  }
  
  // Backend expects plan_id, not plan_name
  // Need to store plan_id when plans are generated
  return request(`/plans/${planId}/select`, {  // CHANGED PATH
    method: 'POST',
  });
}
```

#### **E. Chat Function**

```javascript
export async function sendChatMessage({ message, conversationId, context }) {
  if (USE_MOCK_DATA) {
    await mockDelay(650);
    return normalizeChatResponse(MOCK_CHAT_REPLY);
  }
  
  const data = await request('/chat', {
    method: 'POST',
    body: {
      customer_id: context.profileId,  // ADD
      message,
      session_id: conversationId,  // CHANGED
      include_context: true,
    },
  });
  
  return normalizeChatResponse({
    conversation_id: data.session_id,
    reply: data.message,
  });
}
```

---

## 📝 Complete Updated API Client

Would you like me to:

1. **Create a new `apiClient.js`** with all fixes applied?
2. **Show you a diff/comparison** of what needs to change?
3. **Create a migration script** that updates gradually?

---

## ⚠️ Critical Decisions Needed

### **Decision 1: Missing Endpoints**

**Option A**: Implement missing backend endpoints
- `POST /api/v1/plans/compare` 
- `POST /api/v1/whatif`

**Option B**: Disable features in frontend temporarily
- Hide "Compare Plans" button
- Hide "What-If Analysis" section

**Recommendation**: **Option B** for MVP, add later

---

### **Decision 2: Field Naming Convention**

**Option A**: Update frontend to match backend
- Easier, less work
- Frontend already has normalizers

**Option B**: Add transformation layer in backend
- More work
- Better if multiple frontends will use API

**Recommendation**: **Option A** - Update frontend

---

### **Decision 3: Profile Creation Flow**

Frontend collects: `age, income, expenses, assets, liabilities`
Backend requires: `name, age, occupation, income, expenses, total_assets, total_liabilities`

**Option A**: Add fields to frontend form (name, occupation)
**Option B**: Use default values in API client

**Recommendation**: **Option A** for better UX

---

## 🧪 Testing Checklist

Before switching `VITE_USE_MOCK_DATA=false`:

- [ ] Backend is running on `localhost:8000`
- [ ] Database is seeded with sample data
- [ ] Can access `http://localhost:8000/docs`
- [ ] Can manually test endpoint: `curl http://localhost:8000/health`
- [ ] API client is updated with correct paths
- [ ] Field mappings are implemented
- [ ] Frontend `.env.local` is configured

---

## 🚀 Ready to Integrate?

**Confirm before proceeding**:
1. Do you want me to create the updated `apiClient.js`?
2. Should I implement missing backend endpoints (compare, whatif)?
3. Should I add name/occupation fields to frontend forms?
4. Should I create an integration testing script?

---

## 📞 Next Steps

Reply with:
- ✅ "YES" - Create updated API client and proceed
- 📝 "REVIEW" - Show me detailed changes first
- ⏸️ "WAIT" - I'll review the plan and decide

This ensures no conflicts and maintains clean folder structure!
