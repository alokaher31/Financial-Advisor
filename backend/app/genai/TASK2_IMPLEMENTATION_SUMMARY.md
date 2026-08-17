# Task 2 Implementation Summary: Plan Explainer

## Overview
Task 2 implements the financial plan explainer functionality that takes plan output from `generate_plans()` and generates natural language explanations using the Groq LLM.

## Files Changed/Created

### 1. `backend/app/genai/prompts/plan_explanation_prompt.py` (NEW)
**Purpose**: Contains prompt templates for generating plan explanations.

**Key Functions**:
- `create_plan_explanation_prompt(plan: dict) -> str`
  - Builds a structured prompt with all plan details
  - Formats allocation, gap/surplus/shortfall
  - Includes explicit instructions to NOT calculate, only explain
  - Returns formatted prompt string
  
- `create_system_message() -> str`
  - Returns system message defining the LLM's role as a friendly financial advisor

**Key Features**:
- Detects shortfall/surplus/exact match based on `gap_vs_target` sign
- Formats currency with Indian Rupees (₹)
- Provides clear structure for the LLM response
- Explicitly instructs LLM to use ONLY provided numbers, never calculate

### 2. `backend/app/genai/explainer.py` (NEW)
**Purpose**: Main module for generating plan explanations.

**Key Functions**:
- `explain_plan(plan: Dict[str, Any], temperature=0.7, max_tokens=600) -> str`
  - Validates plan structure
  - Creates prompt using `create_plan_explanation_prompt()`
  - Calls `generate_llm_response()` from `llm_client.py`
  - Returns natural language explanation
  
- `explain_multiple_plans(plans: list, ...) -> list[str]`
  - Convenience function to explain all 3 plans at once
  - Returns list of explanations

**Validation**:
- Checks for all required fields: `plan_name`, `allocation`, `blended_expected_return`, `projected_corpus`, `gap_vs_target`, `required_monthly_investment`, `risk_level`
- Validates allocation is a dictionary
- Raises `ValueError` with clear messages for missing/invalid data

### 3. `backend/tests/test_explainer.py` (NEW)
**Purpose**: Comprehensive unit tests with mocked LLM responses.

**Test Coverage** (18 tests, all passing):
- Prompt generation for different gap scenarios (shortfall, surplus, exact match)
- LLM call parameter validation
- Custom temperature and max_tokens
- Missing/invalid field error handling
- Multiple plan explanation
- Numeric value inclusion in prompts
- System message usage
- Zero investment scenarios
- Instructions to NOT calculate

**Mocking Strategy**:
```python
@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_calls_llm_with_correct_parameters(mock_llm, sample_plan):
    mock_llm.return_value = "Mocked explanation"
    result = explain_plan(sample_plan)
    # Verify LLM was called with correct parameters
```

## Data Flow

### Complete Flow: generate_plans() → explain_plan()

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
     ... (Balanced and Growth)
   ]
   
2. Member 4's Code: explain_plan(plan)
   ↓
   Validates plan structure
   ↓
   create_plan_explanation_prompt(plan)
   → Builds structured prompt with:
     - All plan values formatted
     - Gap status (SHORTFALL/SURPLUS/EXACT MATCH)
     - Clear instructions
   ↓
   create_system_message()
   → Returns system message
   ↓
   generate_llm_response(prompt, system_message, ...)
   → Calls llm_client.py (Task 1)
   → Uses Groq API with openai/gpt-oss-120b
   ↓
   Returns natural language explanation string
```

## How the Prompt is Constructed

### Input Plan:
```python
plan = {
    "plan_name": "Balanced",
    "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
    "blended_expected_return": 9.9,
    "projected_corpus": 3416744.29,
    "gap_vs_target": -1583255.71,
    "required_monthly_investment": 60499.80,
    "risk_level": "Moderate"
}
```

### Generated Prompt Structure:
```
You are a financial advisor explaining a personalized investment plan...

PLAN DETAILS:
- Plan Name: Balanced
- Risk Level: Moderate
- Asset Allocation: Equity: 50%, Debt: 25%, Gold: 15%, Real_Estate: 10%, Cash: 0%
- Blended Expected Return: 9.9% per year
- Projected Corpus: ₹3,416,744.29
- Gap vs Target: SHORTFALL of ₹1,583,255.71
- Required Monthly Investment: ₹60,499.80

INSTRUCTIONS:
1. Start with a brief overview...
2. Explain the asset allocation strategy...
3. Explain what the 9.9% expected return means...
4. Explain the projected corpus...
5. Clearly explain the gap situation (SHORTFALL)...
6. Explain the required monthly investment...
7. End with a brief summary...

IMPORTANT RULES:
- Use ONLY the numbers provided above. DO NOT calculate or invent any new numbers.
- Explain the calculations conceptually, but do not perform mathematical operations.
- Keep the language simple and conversational...
- Use Indian Rupees (₹) as the currency.
- Keep the explanation to 250-350 words.

Please provide the explanation now:
```

## How llm_client.py is Called

```python
# From explainer.py

from .llm_client import generate_llm_response

# Inside explain_plan():
explanation = generate_llm_response(
    prompt=user_prompt,              # Full prompt with plan details
    system_message=system_message,    # System role definition
    temperature=0.7,                  # Default, configurable
    max_tokens=600,                   # Default, configurable
)

# generate_llm_response() internally:
# 1. Gets singleton LLMClient instance
# 2. Calls client.generate_response()
# 3. Which calls Groq API with openai/gpt-oss-120b
# 4. Returns the explanation string
```

## Tests Added and Results

### Test Suite: `tests/test_explainer.py`

**Results**:
```
==================== test session starts ====================
platform win32 -- Python 3.12.4, pytest-9.1.1, pluggy-1.6.0
collected 18 items

tests/test_explainer.py::test_create_plan_explanation_prompt_contains_all_plan_details PASSED [  5%]
tests/test_explainer.py::test_create_plan_explanation_prompt_shows_shortfall PASSED [ 11%]
tests/test_explainer.py::test_create_plan_explanation_prompt_shows_surplus PASSED [ 16%]
tests/test_explainer.py::test_create_plan_explanation_prompt_shows_exact_match PASSED [ 22%]
tests/test_explainer.py::test_create_system_message_returns_string PASSED [ 27%]
tests/test_explainer.py::test_explain_plan_calls_llm_with_correct_parameters PASSED [ 33%]
tests/test_explainer.py::test_explain_plan_returns_string PASSED [ 38%]
tests/test_explainer.py::test_explain_plan_with_custom_temperature PASSED [ 44%]
tests/test_explainer.py::test_explain_plan_with_custom_max_tokens PASSED [ 50%]
tests/test_explainer.py::test_explain_plan_raises_error_for_missing_fields PASSED [ 55%]
tests/test_explainer.py::test_explain_plan_raises_error_for_invalid_allocation PASSED [ 61%]
tests/test_explainer.py::test_explain_multiple_plans PASSED [ 66%]
tests/test_explainer.py::test_explain_multiple_plans_with_custom_parameters PASSED [ 72%]
tests/test_explainer.py::test_explain_plan_prompt_includes_plan_name PASSED [ 77%]
tests/test_explainer.py::test_explain_plan_prompt_includes_all_numeric_values PASSED [ 83%]
tests/test_explainer.py::test_explain_plan_uses_system_message PASSED [ 88%]
tests/test_explainer.py::test_explain_plan_handles_zero_required_investment PASSED [ 94%]
tests/test_explainer.py::test_prompt_instructs_llm_not_to_calculate PASSED [100%]

==================== 18 passed in 0.79s ====================
```

**All 18 tests pass** ✅

### Test Categories:
1. **Prompt Generation Tests** (4 tests)
   - Validates prompt includes all plan details
   - Tests shortfall/surplus/exact match detection
   
2. **LLM Integration Tests** (6 tests)
   - Mocked LLM calls with parameter validation
   - Custom temperature and max_tokens
   - Return value verification
   
3. **Error Handling Tests** (2 tests)
   - Missing required fields
   - Invalid allocation type
   
4. **Multiple Plans Tests** (2 tests)
   - Batch explanation
   - Parameter passing
   
5. **Prompt Content Tests** (4 tests)
   - Plan name inclusion
   - Numeric value inclusion
   - System message usage
   - No-calculation instructions

## Example Output

### Input (from generate_plans):
```python
plan = {
    "plan_name": "Balanced",
    "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
    "blended_expected_return": 9.9,
    "projected_corpus": 3416744.29,
    "gap_vs_target": -1583255.71,
    "required_monthly_investment": 60499.80,
    "risk_level": "Moderate"
}
```

### Output (from explain_plan):
```
The Balanced plan is designed for investors who want a moderate level of risk. 
It isn't as aggressive as a high‑growth plan, but it still aims to grow your 
money faster than a very conservative option.

Your money will be spread across five different buckets:  
- Equity(50%) – half of the portfolio goes into stocks
- Debt(25%) – a quarter is in bonds and fixed‑income instruments
- Gold(15%) – protection against inflation
- Real Estate(10%) – property‑related assets
- Cash(0%) – all money is actively working

The blended expected return of 9.9% per year means that, on average, the 
portfolio is projected to earn just under ten percent annually.

The total value of your investments at the target horizon is expected to be 
₹3,416,744.29.

Your target amount is higher than the projected corpus, resulting in a 
SHORTFALL of ₹1,583,255.71. You would need roughly one and a half million 
rupees more to reach your goal.

To work toward the projected corpus, the plan calls for a required monthly 
investment of ₹60,499.80.

The Balanced plan gives you a moderate‑risk, diversified approach that could 
grow to ₹3.4 million, but it falls short of your target by ₹1.58 million.
```

## Key Design Decisions

1. **No Financial Calculations**: The explainer ONLY explains numbers, never calculates them
2. **Validation First**: All plan fields are validated before LLM call
3. **Mocked Tests**: Tests use mocks to avoid real API calls during testing
4. **Reusable Prompts**: Prompt templates are separate from business logic
5. **Gap Detection**: Automatically determines shortfall/surplus/exact match
6. **Error Messages**: Clear, actionable error messages for missing/invalid data
7. **Configurable LLM**: Temperature and max_tokens can be adjusted per call

## Integration Points

### With Member 2's Code (plan_generator.py):
- Accepts the exact 7-field plan structure
- No modifications to plan data
- Validates all required fields are present

### With Task 1 (llm_client.py):
- Uses `generate_llm_response()` convenience function
- Passes system_message, prompt, temperature, max_tokens
- Relies on retry/fallback logic in llm_client.py

### With Future Members:
- `explainer.py` is imported by API routes
- Can be used for single plan or all 3 plans
- Returns plain string, easy to serialize to JSON

## Files NOT Modified (as required)

✅ `backend/app/core/` - No changes
✅ `backend/app/genai/llm_client.py` - No changes
✅ `backend/app/genai/comparator.py` - No changes
✅ `backend/app/genai/chatbot.py` - No changes
✅ `backend/app/genai/retriever.py` - No changes
✅ Other prompt files - No changes

## Verification Commands

```bash
# Run all explainer tests
cd backend
.\.venv\Scripts\Activate.ps1
$env:PYTHONPATH="$PWD"
python -m pytest tests/test_explainer.py -v

# Test a single explanation with real API
python -c "
from app.core.plan_generator import generate_plans
from app.genai.explainer import explain_plan
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

print(explain_plan(plans[1]))
"
```

## Summary

Task 2 is **complete** and **fully tested**:
- ✅ Created `plan_explanation_prompt.py` with prompt templates
- ✅ Created `explainer.py` with plan explanation logic
- ✅ Reuses existing `llm_client.py` (Task 1)
- ✅ Accepts exact plan structure from `generate_plans()`
- ✅ Never calculates, only explains provided numbers
- ✅ 18 unit tests, all passing
- ✅ Integration tested with real Groq API
- ✅ No modifications to restricted files
