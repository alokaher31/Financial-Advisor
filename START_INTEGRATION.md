# 🚀 START FRONTEND INTEGRATION - Quick Setup Guide

## ⚡ **5-Minute Integration Setup**

Follow these steps **IN ORDER** for efficient integration with zero conflicts.

---

## 📋 **Pre-Flight Checklist** (2 minutes)

### Step 1: Install Backend Dependencies
```bash
cd backend
pip3 install -r requirements.txt
```

**Expected Output**: All packages installed successfully

---

### Step 2: Create Backend Environment File
```bash
cd backend
cp .env.example .env
```

**Then edit `.env` and add your Groq API key**:
```bash
# Use any text editor
nano .env
# OR
open .env
```

Add this line:
```
GROQ_API_KEY=your-actual-groq-api-key-here
```

---

### Step 3: Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

**Expected Output**: Dependencies installed successfully

---

### Step 4: Create Frontend Environment File
```bash
cd frontend
cp .env.example .env.local
```

**Then edit `.env.local`**:
```bash
nano .env.local
# OR
open .env.local
```

Set these values:
```env
VITE_API_BASE_URL=http://localhost:8000
VITE_USE_MOCK_DATA=false
```

---

## 🔧 **Quick Integration Fix** (3 minutes)

### Step 5: Update API Client

**File**: `frontend/src/api/apiClient.js`

**Line 69** - Find this:
```javascript
fetch(`${API_BASE_URL}/api${path}`)
```

**Change to**:
```javascript
fetch(`${API_BASE_URL}/api/v1${path}`)
```

**That's the ONLY change needed to start!** 🎉

---

## 🧪 **Test the Integration** (2 minutes)

### Step 6: Start Backend (Terminal 1)
```bash
cd backend
python3 -m app.db.seed_data
uvicorn app.main:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

**Verify**: Open http://localhost:8000/docs

---

### Step 7: Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

**Expected Output**:
```
VITE ready in XXX ms
Local: http://localhost:5173/
```

**Verify**: Open http://localhost:5173

---

## ✅ **Quick Verification Test**

### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected**: `{"status":"healthy","database":"healthy",...}`

### Test 2: API Connection
Open browser DevTools (F12) → Network tab

Try creating a profile in the frontend UI. You should see:
- ❌ **Before fix**: Request to `/api/profile` → 404 error
- ✅ **After fix**: Request to `/api/v1/profile` → 201 success

---

## 🐛 **Common Issues & Quick Fixes**

### Issue 1: "Module not found" (Backend)
**Solution**:
```bash
cd backend
pip3 install -r requirements.txt
# If still failing:
python3 -m pip install fastapi uvicorn sqlalchemy pydantic
```

### Issue 2: "Cannot find module" (Frontend)
**Solution**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Issue 3: CORS Error
**Solution**: Backend already configured for localhost:5173, just restart:
```bash
# Stop backend (Ctrl+C)
# Start again
uvicorn app.main:app --reload
```

### Issue 4: 404 on API Calls
**Solution**: Make sure you updated line 69 in `apiClient.js`:
```javascript
// Must be /api/v1, not /api
fetch(`${API_BASE_URL}/api/v1${path}`)
```

### Issue 5: Database Error
**Solution**:
```bash
cd backend
rm financial_advisor.db  # Delete old DB
python3 -m app.db.seed_data  # Recreate with data
```

---

## 📊 **What to Expect**

### Working Features ✅
1. **Create Profile** - Should save to database
2. **Risk Assessment** - Should calculate score
3. **Create Goal** - Should calculate required savings
4. **Generate Plans** - Should return 3 plans
5. **Chat** - Should return response (placeholder text)

### Not Working Yet ⚠️
1. **Compare Plans** - Backend endpoint missing
2. **What-If Analysis** - Backend endpoint missing

**Solution**: These features will show errors. Hide the buttons or wait for backend implementation.

---

## 🎯 **Next Steps After Basic Integration**

Once the above works, you can proceed with:

### Level 2: Field Mapping Fixes
- Map `assets` → `total_assets`
- Map `profile_id` → `customer_id`
- Map `goal_id` → `goal_ids` (array)

**Reference**: See `INTEGRATION_GUIDE.md` for detailed mappings

### Level 3: Add Missing Features
- Implement compare plans endpoint
- Implement what-if endpoint
- Add GenAI integration (Member 4)

---

## 📝 **Development Workflow**

```bash
# Terminal 1 - Backend
cd backend
uvicorn app.main:app --reload

# Terminal 2 - Frontend  
cd frontend
npm run dev

# Terminal 3 - Testing/Commands
cd backend
# Run tests, check logs, etc.
```

---

## 🎉 **Success Criteria**

You'll know integration is working when:

1. ✅ Backend shows in logs: `POST /api/v1/profile` → 201
2. ✅ Frontend DevTools shows: Request successful, response received
3. ✅ Data appears in frontend UI from real backend
4. ✅ No mock data messages in UI
5. ✅ Database file grows (data being saved)

---

## 💡 **Pro Tips**

1. **Keep both terminals visible** - Watch logs for errors
2. **Use browser DevTools** - Network tab shows all API calls
3. **Check backend logs first** - Most issues are field mismatches
4. **Start simple** - Get profile working, then add more features
5. **Use sample data** - 5 customers already seeded for testing

---

## 🆘 **Need Help?**

### Check Backend Logs
```bash
# Backend shows all requests
# Look for 4xx/5xx errors
```

### Check Frontend Console
```bash
# Browser DevTools → Console
# Look for API errors
```

### Verify Database
```bash
cd backend
python3 -c "from app.db.database import check_db_connection; print(check_db_connection())"
```

### Test API Directly
```bash
# Test profile creation
curl -X POST http://localhost:8000/api/v1/profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test",
    "age": 30,
    "occupation": "Engineer",
    "monthly_income": 100000,
    "monthly_expenses": 60000,
    "total_assets": 1000000,
    "total_liabilities": 200000
  }'
```

---

## ✅ **Ready to Start?**

**YES!** You can start efficiently with just **ONE simple change**:

1. Update line 69 in `apiClient.js`: `/api` → `/api/v1`
2. Switch to real API: `.env.local` → `VITE_USE_MOCK_DATA=false`
3. Start both servers
4. Test!

**Time needed**: ~10 minutes total

**Difficulty**: Easy (just 1 line change to start)

**Risk**: Very low (can revert anytime)

---

## 🚀 **Let's Go!**

Open 3 terminals and run:

**Terminal 1**:
```bash
cd "/Users/alok/Documents/FINANCIAL ADVISOR/finance-planner/backend"
pip3 install -r requirements.txt
python3 -m app.db.seed_data
uvicorn app.main:app --reload
```

**Terminal 2**:
```bash
cd "/Users/alok/Documents/FINANCIAL ADVISOR/finance-planner/frontend"
npm install
npm run dev
```

**Terminal 3**:
```bash
# Make the API fix
cd "/Users/alok/Documents/FINANCIAL ADVISOR/finance-planner/frontend/src/api"
# Edit apiClient.js line 69
```

**You're ready for efficient integration!** 🎯
