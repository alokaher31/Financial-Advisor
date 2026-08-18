# Prompt Library

All GenAI prompts used in the Financial Advisor application.

---

## 1. Chatbot System Prompt

**File**: `backend/app/genai/prompts/chatbot_system_prompt.py`

**Purpose**: Defines the chatbot's personality, capabilities, and guidelines.

**Input**: Customer context (profile, goals, risk, plans)

**Example**:
```
System: You are an expert financial advisor assistant...

Customer Context:
- Age: 35 years
- Monthly Income: ₹150,000
- Goals: Retirement (₹5 Cr in 25 years)
- Risk Profile: Moderate

User Question: How should I allocate my investments?

Response: Based on your moderate risk profile and 25-year timeline...
```

---

## 2. Plan Explanation Prompt

**File**: `backend/app/genai/prompts/plan_explanation_prompt.py`

**Purpose**: Generates natural language explanation of investment plans.

**Input**: Plan details (allocation, returns, projections)

**Output**: 300-400 word explanation

**Example Input**:
```
Plan: Conservative
Allocation: 40% Equity, 45% Debt, 10% Gold, 5% Real Estate
Expected Return: 8.5%
Projected Corpus: ₹4.5 Cr
Gap vs Target: -₹50 Lakh
```

**Example Output**:
```
The Conservative plan is designed for risk-averse investors...
With a balanced allocation heavily weighted toward debt...
```

---

## 3. Plan Comparison Prompt

**File**: `backend/app/genai/prompts/plan_comparison_prompt.py`

**Purpose**: Compares multiple investment plans side-by-side.

**Input**: 3 plans (Conservative, Moderate, Aggressive)

**Output**: Structured comparison with recommendations

**Example Input**:
```
Conservative: 8.5% return, ₹4.5 Cr corpus
Moderate: 10.2% return, ₹6.2 Cr corpus
Aggressive: 12.0% return, ₹8.5 Cr corpus
```

**Example Output**:
```
KEY DIFFERENCES:

Risk vs Return:
- Conservative offers stability but falls short by ₹50L
- Moderate balances risk and meets your target
- Aggressive maximizes returns but requires high risk tolerance

RECOMMENDATION:
For your moderate risk profile, the Moderate plan...
```

---

## 4. What-If Narration Prompt

**File**: `backend/app/genai/prompts/whatif_narration_prompt.py`

**Purpose**: Explains impact of changing financial parameters.

**Input**: Original plan, adjusted plan, scenario details

**Output**: Narrative explanation of changes

**Example Input**:
```
Scenario: Increase monthly investment from ₹50,000 to ₹70,000

Before:
- Projected Corpus: ₹4.5 Cr
- Gap: -₹50 Lakh

After:
- Projected Corpus: ₹6.3 Cr
- Gap: +₹80 Lakh (SURPLUS)
```

**Example Output**:
```
By increasing your monthly investment by ₹20,000, you transform
a shortfall into a surplus. The additional ₹20,000 compounds over
25 years to generate an extra ₹1.8 Cr...
```

---

## Best Practices

### Prompt Engineering Rules

1. **Be Specific**: Include exact numbers, not ranges
2. **Provide Context**: Always include customer profile
3. **Set Constraints**: Word limits, tone, format
4. **Use Examples**: Show desired output format
5. **Indian Context**: Use ₹, Indian terms (Lakh, Crore)

### Temperature Settings

- **Plan Explanations**: 0.7 (balanced creativity)
- **Comparisons**: 0.6 (focused, structured)
- **What-If**: 0.7 (narrative, engaging)
- **Chatbot**: 0.7 (conversational, helpful)

### Token Limits

- Explanations: 600 tokens
- Comparisons: 800 tokens
- What-If: 600 tokens
- Chatbot: 1000 tokens

---

## Testing Prompts

Use `backend/app/genai/test_prompts.py` (if exists) or test via:

```python
from app.genai.llm_client import get_llm_client

client = get_llm_client()
response = client.generate_response(
    prompt="Your test prompt here",
    system_message="System context",
    temperature=0.7,
    max_tokens=500
)
print(response)
```
