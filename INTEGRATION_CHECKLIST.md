# ✅ Frontend-Backend Integration Checklist

## 🎯 Before You Start

**IMPORTANT**: Read `INTEGRATION_GUIDE.md` first for detailed explanations.

---

## 📋 Pre-Integration Verification

### Backend Status
- [ ] Backend is running: `cd backend && uvicorn app.main:app --reload`
- [ ] API accessible: Visit `http://localhost:8000/docs`
- [ ] Health check passes: `curl http://localhost:8000/health`
- [ ] Database seeded: `python -m app.db.seed_data`
- [ ] Sample data exists: 5 customers, 14 goals

### Frontend Status
- [ ] Frontend dependencies installed: `cd frontend && npm install`
- [ ] Can run in mock mode: `npm run dev`
- [ ] Accessible at: `http://localhost:5173`
- [ ] Mock data works: Create profile, risk assessment, etc.

---

## 🔧 Integration Changes Required

### 1. Environment Configuration
**File**: `frontend/.env.local` (create if doesn't exist)

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
```

**Status**: [ ] Created

---

### 2. API Path Prefix Fix
**File**: `frontend/src/api/apiClient.js`
**Line**: ~69

**Change**:
```javascript
// FROM:
fetch(`${API_BASE_URL}/api${path}`)

// TO:
fetch(`${API_BASE_URL}/api/v1${path}`)
```

**Status**: [ ] Updated

---

### 3. Field Name Mappings

#### A. Profile Creation
**File**: `frontend/src/api/apiClient.js`
**Function**: `createProfile()`

**Issues**:
- Frontend sends: `assets`, `liabilities`
- Backend expects: `total_assets`, `total_liabilities`
- Backend requires: `name`, `occupation` (missing in frontend)

**Fix Required**: [ ] Add field mapping

---

#### B. Risk Assessment
**File**: `frontend/src/api/apiClient.js`
**Function**: `submitRiskAssessment()`

**Issues**:
- Frontend sends: `profile_id`
- Backend expects: `customer_id`
- Frontend sends to: `/api/risk-assessment`
- Backend provides: `/api/v1/risk`

**Fix Required**: [ ] Update field name and path

---

#### C. Generate Plans
**File**: `frontend/src/api/apiClient.js`
**Function**: `generatePlans()`

**Issues**:
- Frontend sends: `profile_id` → Backend needs: `customer_id`
- Frontend sends: `goal_id` (single) → Backend needs: `goal_ids` (array)
- Frontend sends: `risk_category` → Backend uses: `risk_assessment_id`

**Fix Required**: [ ] Update structure

---

#### D. Select Plan
**File**: `frontend/src/api/apiClient.js`
**Function**: `selectPlan()`

**Issues**:
- Frontend sends: `plan_name`
- Backend expects: `plan_id` (in URL path)
- Path mismatch: `/api/plans/select` vs `/api/v1/plans/{id}/select`

**Fix Required**: [ ] Store plan IDs and update path

---

#### E. Chat
**File**: `frontend/src/api/apiClient.js`
**Function**: `sendChatMessage()`

**Issues**:
- Frontend needs to send: `customer_id`
- Field names: `conversationId` → `session_id`

**Fix Required**: [ ] Update field mapping

---

### 4. Missing Backend Endpoints

**❌ Not Implemented**:
1. `POST /api/v1/plans/compare` - Used by `comparePlans()`
2. `POST /api/v1/whatif` - Used by `runWhatIf()`

**Options**:
- [ ] **Option A**: Disable in frontend (hide buttons)
- [ ] **Option B**: Implement in backend (requires work)

**Decision**: _____________

---

## 🎬 Integration Steps

### Phase 1: Prepare (5 minutes)
1. [ ] Stop both frontend and backend if running
2. [ ] Pull latest changes: `git pull origin main`
3. [ ] Review this checklist
4. [ ] Backup current `apiClient.js`: `cp frontend/src/api/apiClient.js frontend/src/api/apiClient.js.backup`

### Phase 2: Update Configuration (2 minutes)
5. [ ] Create `frontend/.env.local` with correct settings
6. [ ] Verify backend is configured for CORS (already done)

### Phase 3: Update API Client (15 minutes)
7. [ ] Fix API path prefix (`/api` → `/api/v1`)
8. [ ] Update `createProfile()` function
9. [ ] Update `submitRiskAssessment()` function
10. [ ] Update `generatePlans()` function
11. [ ] Update `selectPlan()` function
12. [ ] Update `sendChatMessage()` function
13. [ ] Comment out or disable `comparePlans()` and `runWhatIf()`

### Phase 4: Test (20 minutes)
14. [ ] Start backend: `cd backend && uvicorn app.main:app --reload`
15. [ ] Start frontend: `cd frontend && npm run dev`
16. [ ] **Test 1**: Create profile
17. [ ] **Test 2**: Submit risk assessment
18. [ ] **Test 3**: Create goal
19. [ ] **Test 4**: Generate plans
20. [ ] **Test 5**: Select a plan
21. [ ] **Test 6**: Chat with advisor

### Phase 5: Debug (If Needed)
22. [ ] Check browser console for errors
23. [ ] Check backend logs for API errors
24. [ ] Verify network requests in browser DevTools
25. [ ] Check response data structure matches expectations

### Phase 6: Commit (5 minutes)
26. [ ] Test complete flow end-to-end
27. [ ] Stage changes: `git add frontend/src/api/apiClient.js frontend/.env.local`
28. [ ] Commit: `git commit -m "feat: integrate frontend with backend API"`
29. [ ] Push: `git push origin main`

---

## 🐛 Common Issues & Solutions

### Issue 1: CORS Error
**Symptom**: Browser console shows CORS policy error
**Solution**: 
- Check backend `app/config.py` has `http://localhost:5173` in CORS_ORIGINS
- Restart backend after config changes

### Issue 2: 404 Not Found
**Symptom**: `POST /api/profile` returns 404
**Solution**: 
- Verify API path prefix is `/api/v1` in apiClient.js
- Check backend is running on correct port (8000)

### Issue 3: 422 Validation Error
**Symptom**: Backend returns validation error
**Solution**: 
- Check field names match backend expectations
- Verify all required fields are sent
- Check data types (numbers vs strings)

### Issue 4: Network Error
**Symptom**: "Unable to reach the backend"
**Solution**: 
- Verify backend is running: `curl http://localhost:8000/health`
- Check API_BASE_URL in `.env.local`
- Restart both frontend and backend

### Issue 5: Mock Data Still Shows
**Symptom**: Still seeing mock data after switching
**Solution**: 
- Verify `VITE_USE_MOCK_DATA=false` in `.env.local`
- Restart Vite dev server (Ctrl+C and `npm run dev`)
- Clear browser cache

---

## 📊 Integration Status Dashboard

| Component | Status | Notes |
|-----------|--------|-------|
| **Environment Config** | ⏳ Pending | Create `.env.local` |
| **API Path Prefix** | ⏳ Pending | Update to `/api/v1` |
| **Profile Endpoint** | ⏳ Pending | Field mapping needed |
| **Risk Endpoint** | ⏳ Pending | Field names + path |
| **Goal Endpoint** | ⏳ Pending | Minor adjustments |
| **Plans Endpoint** | ⏳ Pending | Structure changes |
| **Chat Endpoint** | ⏳ Pending | Field mapping |
| **Compare Plans** | ❌ Missing | Backend not implemented |
| **What-If** | ❌ Missing | Backend not implemented |

**Legend**:
- ✅ Complete
- ⏳ Pending
- ❌ Missing/Blocked
- ⚠️ Needs Review

---

## 🚦 Integration Decision Point

**STOP! Before proceeding, answer:**

1. **Do you want me to create the updated `apiClient.js` automatically?**
   - ✅ YES - I'll create it with all fixes
   - ⏸️ NO - I want to review changes first

2. **How to handle missing endpoints (compare, whatif)?**
   - 🚫 Disable features in frontend for now
   - 🔨 Implement backend endpoints first

3. **How to handle missing profile fields (name, occupation)?**
   - 📝 Add fields to frontend form
   - 🎲 Use default/placeholder values

---

## 📞 Ready to Proceed?

Reply with one of:
- **"AUTO"** - Automatically create updated apiClient.js
- **"MANUAL"** - Show me step-by-step what to change
- **"REVIEW"** - I need to review the plan more carefully

**Current Recommendation**: Start with **"REVIEW"** mode, then proceed to **"AUTO"**
