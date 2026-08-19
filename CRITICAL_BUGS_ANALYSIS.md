# Critical Bugs Analysis & Fix Plan

## Issues Identified from Screenshots

### 1. ❌ Corpus Magnitude Bug (CRITICAL)
**Observed**: Plans show ₹35.17 crore, ₹51.06 crore, ₹63.62 crore with required monthly investment of only ₹32, ₹20, ₹14

**Root Cause**: The compounding rate calculation is using **annual rate as decimal** (e.g., 0.12) instead of **percentage points** (e.g., 12.0)

**Evidence**:
- goal_calculator.py expects: `annual_return_rate: 12.0` (percentage points)
- Returns are being passed as: `0.12` (decimal)
- Formula: `monthly_rate = annual_rate / 100 / 12`
- If passed `0.12` → `0.12 / 100 / 12 = 0.0001` (tiny rate, no growth)
- If passed `12.0` → `12.0 / 100 / 12 = 0.01` (1% monthly, correct)

**Where to Fix**:
1. Check `plan_generator.py` - ensure returns_by_asset is in percentage points
2. Check `data_loader.py` - ensure CSV has returns as 12.0, not 0.12
3. Check whatif_analyzer.py - ensure consistent unit handling

---

###2. ❌ Divergent Calculation Paths (CRITICAL)
**Observed**: 
- Plans page: Growth plan corpus = ₹63,62,01,248
- What-If panel: Same Growth plan Before state = ₹10,60,56,887
- Difference: 6x discrepancy!

**Root Cause**: Two different code paths:
1. `/plans/generate` endpoint (plan_routes.py) → uses plan_generator.py
2. `/whatif` endpoint (plan_routes.py) → uses whatif_analyzer.py

These likely use different:
- Return rates (one correct, one wrong)
- Time horizons
- Contribution amounts

**Where to Fix**:
- Trace both endpoints
- Ensure both call the SAME goal_calculator functions
- Verify both use the SAME return rate source

---

### 3. ❌ Chatbot Fabricating Numbers (ARCHITECTURE VIOLATION)
**Observed**: Chatbot created a complete projection table showing:
```
Current: 20% gold, ₹5L projected
Adjusted: 10% gold, ₹5.4L projected
```

**Root Cause**: 
- LLM invented these numbers from scratch
- No backend endpoint for "what-if allocation change" exists
- Only "what-if monthly investment change" is implemented
- **VIOLATES CORE PRINCIPLE**: "Python calculates numbers, never the LLM"

**Where to Fix**:
1. Add strict guardrails to chatbot system prompt:
   - "NEVER generate financial projections yourself"
   - "NEVER create tables with specific rupee amounts"
   - "If asked about allocation changes, say 'This feature is coming soon'"
2. Implement proper allocation-change what-if endpoint (or explicitly block it)

---

### 4. ❌ Risk Level Mislabeling (DATA BUG)
**Observed**: AI comparison says "All three plans are labeled 'Conservative'"

**Reality**: UI badges correctly show CONSERVATIVE / MODERATE / AGGRESSIVE

**Root Cause**: 
- `plan_generator.py` correctly sets `risk_level` per plan
- `comparator.py` is receiving wrong data OR
- Loop bug where all 3 plans get the same risk_level value

**Where to Fix**:
- Check plan_routes.py's /plans/compare endpoint
- Verify it's passing 3 distinct plan objects to comparator
- Not reusing the same plan object 3 times

---

### 5. ✅ Number Formatting (Cosmetic, Low Priority)
**Observed**: LLM writes `₹351,764,362.19` (Western) vs cards show `₹35,17,64,362` (Indian)

**Not a bug**: Same number, different formatting
**Fix**: Apply consistent Indian lakh/crore formatting in LLM responses

---

## Terminology Simplification (User Request)

### Remove "Corpus" - Use Customer-Friendly Terms

**Current Terms** → **New Terms**:
- `projected_corpus` → `total_savings` or `final_amount`
- `gap_vs_target` → `shortfall` (negative) / `surplus` (positive)
- `required_monthly_investment` → `monthly_savings_needed`
- `blended_expected_return` → `expected_growth_rate`

**Where to Update**:
1. Frontend display labels (PlanCard.jsx, WhatIfPanel.jsx)
2. API response field names (keep backend as-is for consistency, map in frontend)
3. LLM prompts (chatbot_system_prompt.py, plan_explanation_prompt.py)

---

## Fix Priority Order

### Phase 1: Critical Data Bugs (MUST FIX NOW)
1. ✅ **Fix corpus magnitude bug** - Verify return rate units
2. ✅ **Fix divergent paths** - Make What-If use same calculator
3. ✅ **Block chatbot number fabrication** - Add strict guardrails

### Phase 2: Data Quality (HIGH PRIORITY)
4. ✅ **Fix risk level mislabeling** - Ensure correct risk values passed to comparator

### Phase 3: User Experience (MEDIUM PRIORITY)
5. ✅ **Simplify terminology** - Remove "corpus", use plain language
6. ⏸️ **Number formatting** - Apply Indian grouping consistently (cosmetic)

---

## Testing Plan

### Test Case 1: Verify Return Rate Units
```python
# In plan_generator.py, add logging:
logger.info(f"Returns by asset: {returns_by_asset}")
# Expected: {'Equity': 12.0, 'Debt': 8.0, ...}
# NOT: {'Equity': 0.12, 'Debt': 0.08, ...}
```

### Test Case 2: Compare Both Endpoints
```bash
# Generate plans
curl /api/v1/plans/generate -d '{"customer_id":1, "goal_id":1}'
# Note Growth plan corpus value

# Run what-if on same plan
curl /api/v1/plans/whatif -d '{"plan_id":X, "scenario": {...}}'
# Verify "Before" corpus matches plan corpus ± small delta
```

### Test Case 3: Chatbot Guardrails
```bash
# Ask chatbot to create numbers
curl /api/v1/chat/ -d '{"message": "What if I change my gold allocation to 5%?"}'
# Expected: "I can't calculate that" NOT a fabricated table
```

### Test Case 4: Risk Level Verification
```python
# In comparator.py, add logging:
logger.info(f"Plan risk levels: {[p['risk_level'] for p in plans]}")
# Expected: ['Conservative', 'Moderate', 'Aggressive']
# NOT: ['Conservative', 'Conservative', 'Conservative']
```

---

## Implementation Notes

- **DO NOT** guess at fixes - trace actual values through the code
- **ADD** logging/print statements to verify data flow
- **TEST** with real API calls, not just code review
- **VERIFY** numbers in UI match backend responses exactly
- **DOCUMENT** any assumptions or design decisions

---

## Success Criteria

✅ Plans show realistic corpus values (₹10-50 lakhs, not crores)
✅ Required monthly investment is realistic (₹5k-50k, not ₹20)
✅ What-If "Before" matches Plans page within 1%
✅ Chatbot never generates specific rupee projections
✅ AI comparison correctly lists all 3 risk levels
✅ UI uses simple terms: "Total Savings", "Shortfall", "Monthly Savings Needed"
