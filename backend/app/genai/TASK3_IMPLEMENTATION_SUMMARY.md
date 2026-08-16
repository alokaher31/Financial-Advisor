# Task 3 Implementation Summary: Plan Comparator

## Overview
Task 3 implements the financial plan comparator functionality that takes all 3 plans from `generate_plans()` and generates a comprehensive side-by-side comparison using the Groq LLM.

## Files Changed/Created

### 1. `backend/app/genai/prompts/plan_comparison_prompt.py` (NEW)
**Purpose**: Contains prompt templates for comparing three financial plans.

**Key Functions**:
- `create_plan_comparison_prompt(plans: list[dict]) -> str`
  - Validates exactly 3 plans provided
  - Formats all plan details side-by-side with visual separators
  - Detects shortfall/surplus/exact match for each plan
  - Creates structured comparison instructions for 8 key areas
  - Returns formatted prompt string
  
- `create_system_message() -> str`
  - Returns system message defining the LLM's role as an objective comparison advisor

**Key Features**:
- Side-by-side presentation of all three plans with visual separators
- Automatic gap detection (shortfall/surplus/exact match) for each plan
- Comprehensive comparison instructions covering:
  1. Risk level comparison
  2. Asset allocation differences
  3. Expected return comparison
  4. Projected corpus comparison
  5. Gap analysis comparison
  6. Required investment comparison
  7. Trade-offs summary
  8. Recommendation guidance
- Explicit instructions to NOT calculate, only compare and explain
- Objective tone - no pushing of specific plans

### 2. `backend/app/genai/comparator.py` (NEW)
**Purpose**: Main module for generating plan comparisons.

**Key Functions**:
- `compare_plans(plans: List[Dict[str, Any]], temperature=0.7, max_tokens=800) -> str`
  - Validates list of exactly 3 plans
  - Checks all required fields in each plan
  - Creates comparison prompt using `create_plan_comparison_prompt()`
  - Calls `generate_llm_response()` from `llm_client.py`
  - Returns natural language comparison
  
- `compare_plans_structured(plans, ...) -> Dict[str, Any]`
  - Convenience function returning structured response
  - Includes original plans + comparison text + extracted metadata

**Validation**:
- Checks for exactly 3 plans
- Validates each plan has all 7 required fields
- Validates allocation is a dictionary
- Raises `ValueError` with clear messages for invalid data

### 3. `backend/tests/test_comparator.py` (NEW)
**Purpose**: Comprehensive unit tests with mocked LLM responses.

**Test Coverage** (24 tests, all passing):
- Prompt generation for different gap scenarios
- LLM call parameter validation
- Custom temperature and max_tokens
- Plan count validation (must be 3)
- Missing/invalid field error handling
- Trade-offs instruction inclusion
- Structured response format
- Zero investment scenarios
- Instructions to NOT calculate

**Mocking Strategy**:
```python
@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_calls_llm_with_correct_parameters(mock_llm, sample_plans):
    mock_llm.return_value = "Mocked comparison"
    result = compare_plans(sample_plans)
    # Verify LLM was called with correct parameters
```

---

## Data Flow

### Complete Flow: generate_plans() → compare_plans()

```
1. Member 2's Code: generate_plans()
   ↓
   Returns list[dict] with 3 plans:
   [
     {
       "plan_name": "Conservative",
       "allocation": {"Equity": 20, "Debt": 50, ...},
       "blended_expected_return": 8.33,
       "projected_corpus": 3266924.06,
       "gap_vs_target": -1733075.94,
       "required_monthly_investment": 63387.50,
       "risk_level": "Conservative"
     },
     {
       "plan_name": "Balanced",
       ... (similar structure)
     },
     {
       "plan_name": "Growth",
       ... (similar structure)
     }
   ]
   
2. Member 4's Code: compare_plans(plans)
   ↓
   Validates 3 plans with all required fields
   ↓
   create_plan_comparison_prompt(plans)
   → Builds structured comparison prompt with:
     - All 3 plans formatted side-by-side
     - Gap status for each (SHORTFALL/SURPLUS/EXACT MATCH)
     - 8 detailed comparison instructions
     - Clear rules to not calculate
   ↓
   create_system_message()
   → Returns objective advisor role definition
   ↓
   generate_llm_response(prompt, system, temp, tokens)
   → Calls llm_client.py (Task 1)
   → Uses Groq API with openai/gpt-oss-120b
   ↓
   Returns comprehensive comparison string
```

---

## How Three Plan Dictionaries Flow into comparator.py

### Input: Three Plans from generate_plans()
```python
plans = [
    {
        "plan_name": "Conservative",
        "allocation": {"Equity": 20, "Debt": 50, "Gold": 15, "Real_Estate": 10, "Cash": 5},
        "blended_expected_return": 8.33,
        "projected_corpus": 3266924.06,
        "gap_vs_target": -1733075.94,
        "required_monthly_investment": 63387.50,
        "risk_level": "Conservative"
    },
    {
        "plan_name": "Balanced",
        "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        "blended_expected_return": 9.9,
        "projected_corpus": 3416744.29,
        "gap_vs_target": -1583255.71,
        "required_monthly_investment": 60499.80,
        "risk_level": "Moderate"
    },
    {
        "plan_name": "Growth",
        "allocation": {"Equity": 70, "Debt": 10, "Gold": 10, "Real_Estate": 10, "Cash": 0},
        "blended_expected_return": 10.8,
        "projected_corpus": 3506225.89,
        "gap_vs_target": -1493774.11,
        "required_monthly_investment": 58885.51,
        "risk_level": "Aggressive"
    }
]
```

### Processing Flow:
```python
# 1. Call compare_plans()
comparison = compare_plans(plans)

# 2. Inside compare_plans():
#    - Validate len(plans) == 3
#    - Validate each plan has 7 required fields
#    - Validate each allocation is dict

# 3. Create prompt
#    - Extract plan1, plan2, plan3 from list
#    - Format each plan's details
#    - Detect gap status for each
#    - Build comprehensive comparison instructions

# 4. Call LLM
#    - generate_llm_response(prompt, system_message, ...)
#    - Returns comparison text

# 5. Return comparison string
```

---

## How the Comparison Prompt is Constructed

### Generated Prompt Structure:
```
You are a financial advisor helping a customer compare three different investment plan options...

PLAN COMPARISON:

═══════════════════════════════════════════════════════════════════════════════
PLAN 1: Conservative
═══════════════════════════════════════════════════════════════════════════════
Risk Level: Conservative
Asset Allocation: Equity: 20%, Debt: 50%, Gold: 15%, Real_Estate: 10%, Cash: 5%
Expected Annual Return: 8.33%
Projected Future Value: ₹3,266,924.06
Gap vs Target: SHORTFALL of ₹1,733,075.94
Required Monthly Investment: ₹63,387.50

═══════════════════════════════════════════════════════════════════════════════
PLAN 2: Balanced
═══════════════════════════════════════════════════════════════════════════════
Risk Level: Moderate
Asset Allocation: Equity: 50%, Debt: 25%, Gold: 15%, Real_Estate: 10%, Cash: 0%
Expected Annual Return: 9.9%
Projected Future Value: ₹3,416,744.29
Gap vs Target: SHORTFALL of ₹1,583,255.71
Required Monthly Investment: ₹60,499.80

═══════════════════════════════════════════════════════════════════════════════
PLAN 3: Growth
═══════════════════════════════════════════════════════════════════════════════
Risk Level: Aggressive
Asset Allocation: Equity: 70%, Debt: 10%, Gold: 10%, Real_Estate: 10%, Cash: 0%
Expected Annual Return: 10.8%
Projected Future Value: ₹3,506,225.89
Gap vs Target: SHORTFALL of ₹1,493,774.11
Required Monthly Investment: ₹58,885.51

═══════════════════════════════════════════════════════════════════════════════

INSTRUCTIONS:

1. **Risk Level Comparison**
   Compare the three risk levels (Conservative, Moderate, Aggressive)...

2. **Asset Allocation Differences**
   Explain how the asset mix differs:
   - How much equity exposure changes from Conservative to Growth
   - How debt, gold, real estate, and cash allocations shift...

3. **Expected Return Comparison**
   Compare the expected returns (8.33%, 9.9%, 10.8%)...

4. **Projected Corpus Comparison**
   Compare the projected future values...

5. **Gap Analysis Comparison**
   Compare how each plan performs against the target:
   - Conservative: SHORTFALL of ₹1,733,075.94
   - Balanced: SHORTFALL of ₹1,583,255.71
   - Growth: SHORTFALL of ₹1,493,774.11

6. **Required Investment Comparison**
   Compare the monthly investment requirements...

7. **Trade-offs Summary**
   Clearly explain the key trade-offs:
   - What you gain by moving from Conservative to Balanced to Growth
   - What you risk by choosing higher-growth plans...

8. **Recommendation Guidance**
   End with guidance on how to choose based on:
   - Risk tolerance
   - Time horizon
   - Financial goals
   - Monthly investment capacity

CRITICAL RULES:
- Use ONLY the numbers provided above. DO NOT calculate, modify, or invent any new numbers.
- Explain the differences conceptually. Do not perform mathematical operations.
- Keep the language simple and conversational...
- Use Indian Rupees (₹) as the currency.
- Be objective - don't push one plan over another, explain trade-offs neutrally.
- Keep the comparison to 400-500 words.

Please provide the comparison now:
```

---

## How llm_client.py is Called

```python
# From comparator.py

from .llm_client import generate_llm_response

# Inside compare_plans():
comparison = generate_llm_response(
    prompt=user_prompt,              # Full comparison prompt with 3 plans
    system_message=system_message,    # "You are a financial advisor who compares..."
    temperature=0.7,                  # Default, configurable
    max_tokens=800,                   # Default, configurable (higher for comparison)
)

# generate_llm_response() internally:
# 1. Gets singleton LLMClient instance
# 2. Calls client.generate_response()
# 3. Which calls Groq API with openai/gpt-oss-120b
# 4. Returns the comparison string
```

---

## Test Results

### Test Suite: `tests/test_comparator.py`

```
==================== test session starts ====================
collected 24 items

test_create_plan_comparison_prompt_contains_all_plan_details PASSED
test_create_plan_comparison_prompt_shows_shortfalls PASSED
test_create_plan_comparison_prompt_shows_surplus PASSED
test_create_plan_comparison_prompt_shows_allocation_differences PASSED
test_create_plan_comparison_prompt_raises_error_for_wrong_count PASSED
test_create_system_message_returns_string PASSED
test_compare_plans_calls_llm_with_correct_parameters PASSED
test_compare_plans_returns_string PASSED
test_compare_plans_with_custom_temperature PASSED
test_compare_plans_with_custom_max_tokens PASSED
test_compare_plans_raises_error_for_wrong_plan_count PASSED
test_compare_plans_raises_error_for_non_list PASSED
test_compare_plans_raises_error_for_missing_fields PASSED
test_compare_plans_raises_error_for_invalid_allocation PASSED
test_compare_plans_prompt_includes_all_plan_names PASSED
test_compare_plans_prompt_includes_trade_offs_instruction PASSED
test_compare_plans_uses_system_message PASSED
test_compare_plans_structured_returns_dict PASSED
test_compare_plans_structured_includes_original_plans PASSED
test_compare_plans_structured_extracts_plan_names PASSED
test_compare_plans_structured_extracts_risk_levels PASSED
test_compare_plans_structured_includes_comparison_text PASSED
test_prompt_instructs_llm_not_to_calculate PASSED
test_compare_plans_with_zero_required_investment PASSED

==================== 24 passed in 0.64s ====================
```

**✅ ALL 24 TESTS PASS**

### Test Categories:
1. **Prompt Generation Tests** (5 tests)
   - All plan details included
   - Shortfall/surplus detection
   - Allocation differences
   
2. **LLM Integration Tests** (7 tests)
   - Mocked LLM calls with parameter validation
   - Custom temperature and max_tokens
   - Return value verification
   
3. **Error Handling Tests** (4 tests)
   - Plan count validation (must be 3)
   - Missing required fields
   - Invalid allocation type
   - Non-list input
   
4. **Prompt Content Tests** (4 tests)
   - Plan names inclusion
   - Trade-offs instruction
   - System message usage
   - No-calculation instructions
   
5. **Structured Response Tests** (4 tests)
   - Dictionary format
   - Original plans included
   - Metadata extraction
   - Comparison text inclusion

---

## Example Output

### Input (from generate_plans):
```python
plans = [
    # Conservative plan with 8.33% return, ₹3,266,924 corpus, ₹1,733,076 shortfall
    # Balanced plan with 9.9% return, ₹3,416,744 corpus, ₹1,583,256 shortfall
    # Growth plan with 10.8% return, ₹3,506,226 corpus, ₹1,493,774 shortfall
]
```

### Output (from compare_plans):
```
**1. Risk‑Level Comparison**  
- Conservative – This is the safest of the three. The portfolio is weighted toward 
  debt and cash, which tend to move less sharply when markets swing.
- Balanced (Moderate) – A middle‑ground approach. It adds a larger share of equities 
  while still keeping a solid base of debt.
- Aggressive (Growth) – The highest‑risk option. Most of the money is placed in 
  equities, which can rise quickly but also fall sharply.

**2. Asset‑Allocation Differences**  
- Equity exposure rises from 20% in Conservative to 70% in Growth.
- Debt falls from 50% (Conservative) to 10% (Growth).
- Gold stays steady at 15% for both Conservative and Balanced, then drops to 10% in Growth.
- Real‑estate remains constant at 10% across all three plans.
- Cash is present only in the Conservative plan (5%).

**3. Expected Return Comparison**  
- Conservative: 8.33%  
- Balanced: 9.9%  
- Growth: 10.8%  
The rise in expected return follows the increase in equity weight.

**4. Projected Corpus Comparison**  
- Conservative: ₹3,266,924.06  
- Balanced: ₹3,416,744.29  
- Growth: ₹3,506,225.89  
The Growth plan yields the largest projected future value.

**5. Gap‑Analysis Comparison**  
- Conservative shortfall: ₹1,733,075.94  
- Balanced shortfall: ₹1,583,255.71  
- Growth shortfall: ₹1,493,774.11  
The Growth plan comes closest to the target.

**6. Required Investment Comparison**  
- Conservative: ₹63,387.50 per month  
- Balanced: ₹60,499.80 per month  
- Growth: ₹58,885.51 per month

**7. Trade-offs Summary**  
Moving from Conservative to Growth increases potential returns but also increases 
market volatility. The Conservative plan protects capital better during downturns 
but grows slower. The Growth plan can build wealth faster but requires tolerance 
for larger swings.

**8. Recommendation Guidance**  
Choose based on: your comfort with market volatility, how long you can stay invested, 
whether you can afford higher monthly contributions, and how important it is to 
reach the exact target versus having a stable, predictable plan.
```

---

## Key Design Decisions

1. **Exactly 3 Plans Required**: Validation ensures exactly 3 plans (Conservative, Balanced, Growth)
2. **Side-by-Side Comparison**: Visual separators make it easy to compare plans
3. **8 Comparison Areas**: Comprehensive coverage of all important factors
4. **Objective Tone**: Instructions emphasize neutrality, not pushing any plan
5. **Trade-offs Focus**: Explicitly asks LLM to explain gains and risks
6. **No Calculations**: LLM only compares and explains, never calculates
7. **Structured Option**: `compare_plans_structured()` returns plans + comparison + metadata
8. **Higher Token Limit**: Default 800 tokens (vs 600 for explainer) for comprehensive comparison

---

## Integration Points

### With Member 2's Code (plan_generator.py):
- Accepts list of 3 plans from `generate_plans()`
- No modifications to plan data
- Validates all plans have required 7 fields

### With Task 1 (llm_client.py):
- Uses `generate_llm_response()` convenience function
- Passes system_message, prompt, temperature, max_tokens
- Relies on retry/fallback logic in llm_client.py

### With Task 2 (explainer.py):
- Can be used alongside explainer
- Explainer explains one plan, comparator compares all three
- Both use same llm_client.py and follow same patterns

### With Future Members:
- `comparator.py` will be imported by API routes
- `compare_plans()` for simple comparison text
- `compare_plans_structured()` for JSON-friendly response
- Returns plain string, easy to serialize

---

## Files NOT Modified (as required)

✅ `backend/app/core/` - No changes
✅ `backend/app/genai/llm_client.py` - No changes (Task 1)
✅ `backend/app/genai/explainer.py` - No changes (Task 2)
✅ `backend/app/genai/prompts/plan_explanation_prompt.py` - No changes (Task 2)
✅ `backend/app/genai/chatbot.py` - No changes
✅ `backend/app/genai/retriever.py` - No changes
✅ `backend/app/genai/prompts/whatif_narration_prompt.py` - No changes
✅ Other files - No changes

---

## Verification Commands

```bash
# Run all comparator tests
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="$PWD"
python -m pytest tests/test_comparator.py -v

# Test comparison with real API
python -c "
from app.core.plan_generator import generate_plans
from app.genai.comparator import compare_plans
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

data = pd.DataFrame({
    'asset_category': ['Equity', 'Debt', 'Gold', 'Real_Estate', 'Cash'],
    'avg_annual_return': [12.0, 7.0, 9.0, 8.0, 5.5],
    'volatility': [18.0, 4.0, 12.0, 8.0, 1.0]
})

plans = generate_plans(
    {'monthly_income': 100000, 'monthly_expenses': 60000},
    'Moderate',
    {'target_amount': 5000000, 'current_amount': 200000, 'time_horizon_years': 5},
    data
)

print(compare_plans(plans))
"
```

---

## Summary

Task 3 is **complete** and **fully tested**:
- ✅ Created `plan_comparison_prompt.py` with comparison templates
- ✅ Created `comparator.py` with plan comparison logic
- ✅ Reuses existing `llm_client.py` (Task 1)
- ✅ Accepts exact 3-plan structure from `generate_plans()`
- ✅ Compares all key aspects: risk, allocation, returns, corpus, gap, investment, trade-offs
- ✅ Never calculates, only compares and explains provided numbers
- ✅ 24 unit tests, all passing
- ✅ Integration tested with real Groq API
- ✅ No modifications to restricted files
- ✅ Follows same patterns as Task 2 (explainer)
