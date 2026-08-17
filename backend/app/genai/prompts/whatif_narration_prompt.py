"""
Prompt template for narrating What-If scenario analysis results.
"""


def create_whatif_narration_prompt(whatif_result: dict) -> str:
    """
    Create a prompt for the LLM to narrate a What-If scenario analysis.
    
    Args:
        whatif_result: Dictionary containing What-If analysis results with:
            - scenario_name: str
            - scenario_type: str
            - adjustments: dict with parameter, original_value, adjusted_value, change
            - base_plan: dict with plan details
            - adjusted_plan: dict with plan details
            - impact: dict with corpus_change, gap_change, investment_change, gap_improvement
    
    Returns:
        A formatted prompt string for the LLM to narrate the What-If scenario.
    """
    
    # Extract key information
    scenario_name = whatif_result["scenario_name"]
    adjustments = whatif_result["adjustments"]
    base_plan = whatif_result["base_plan"]
    adjusted_plan = whatif_result["adjusted_plan"]
    impact = whatif_result["impact"]
    
    # Determine gap status for base and adjusted
    def format_gap_status(gap: float) -> tuple[str, float]:
        if gap < 0:
            return "SHORTFALL", abs(gap)
        elif gap > 0:
            return "SURPLUS", gap
        else:
            return "EXACT MATCH", 0.0
    
    base_gap_status, base_gap_amount = format_gap_status(base_plan["gap_vs_target"])
    adjusted_gap_status, adjusted_gap_amount = format_gap_status(adjusted_plan["gap_vs_target"])
    
    # Determine if gap improved
    improvement_text = "IMPROVED" if impact["gap_improvement"] else "WORSENED"
    
    prompt = f"""You are a financial advisor explaining a "What-If" scenario analysis to a customer. 
Your goal is to help them understand how a change in their situation would impact their financial plan.

WHAT-IF SCENARIO ANALYSIS:

═══════════════════════════════════════════════════════════════════════════════
SCENARIO: {scenario_name}
═══════════════════════════════════════════════════════════════════════════════

ADJUSTMENT MADE:
  Parameter Changed: {adjustments['parameter']}
  Original Value: ₹{adjustments['original_value']:,.2f}
  Adjusted Value: ₹{adjustments['adjusted_value']:,.2f}
  Change: ₹{adjustments['change']:,.2f}

═══════════════════════════════════════════════════════════════════════════════
BASE SCENARIO (Before Adjustment)
═══════════════════════════════════════════════════════════════════════════════
Plan: {base_plan['plan_name']} ({base_plan['risk_level']} Risk)
Asset Allocation: {', '.join(f"{asset}: {pct}%" for asset, pct in base_plan['allocation'].items())}
Expected Annual Return: {base_plan['blended_expected_return']}%
Projected Future Value: ₹{base_plan['projected_corpus']:,.2f}
Gap vs Target: {base_gap_status} of ₹{base_gap_amount:,.2f}
Required Monthly Investment: ₹{base_plan['required_monthly_investment']:,.2f}

═══════════════════════════════════════════════════════════════════════════════
ADJUSTED SCENARIO (After Adjustment)
═══════════════════════════════════════════════════════════════════════════════
Plan: {adjusted_plan['plan_name']} ({adjusted_plan['risk_level']} Risk)
Asset Allocation: {', '.join(f"{asset}: {pct}%" for asset, pct in adjusted_plan['allocation'].items())}
Expected Annual Return: {adjusted_plan['blended_expected_return']}%
Projected Future Value: ₹{adjusted_plan['projected_corpus']:,.2f}
Gap vs Target: {adjusted_gap_status} of ₹{adjusted_gap_amount:,.2f}
Required Monthly Investment: ₹{adjusted_plan['required_monthly_investment']:,.2f}

═══════════════════════════════════════════════════════════════════════════════
IMPACT OF THE ADJUSTMENT
═══════════════════════════════════════════════════════════════════════════════
Projected Corpus Change: ₹{impact['corpus_change']:,.2f}
Gap Change: ₹{impact['gap_change']:,.2f} ({improvement_text})
Required Monthly Investment Change: ₹{impact['investment_change']:,.2f}

═══════════════════════════════════════════════════════════════════════════════

INSTRUCTIONS:

1. **Introduce the Scenario**
   Start by clearly stating what change is being explored: {scenario_name}

2. **Explain the Adjustment**
   Describe what parameter changed:
   - From ₹{adjustments['original_value']:,.2f} to ₹{adjustments['adjusted_value']:,.2f}
   - A change of ₹{adjustments['change']:,.2f}
   - What this means in practical terms

3. **Compare Base vs Adjusted Outcomes**
   Explain the impact on key metrics:
   - Projected corpus changed from ₹{base_plan['projected_corpus']:,.2f} to ₹{adjusted_plan['projected_corpus']:,.2f}
   - A difference of ₹{impact['corpus_change']:,.2f}
   - Gap changed from {base_gap_status} of ₹{base_gap_amount:,.2f} to {adjusted_gap_status} of ₹{adjusted_gap_amount:,.2f}
   - Required monthly investment changed from ₹{base_plan['required_monthly_investment']:,.2f} to ₹{adjusted_plan['required_monthly_investment']:,.2f}

4. **Explain Why This Happened**
   Connect the adjustment to the outcomes:
   - Why did the adjustment lead to these changes?
   - What's the cause-and-effect relationship?

5. **Assess the Impact**
   Clearly state whether this adjustment helps or hurts:
   - Is the gap improvement positive ({improvement_text})?
   - Did the projected corpus increase or decrease?
   - What does this mean for reaching the financial goal?

6. **Provide Actionable Insight**
   End with practical guidance:
   - Is this adjustment realistic/achievable?
   - Should the customer consider this change?
   - What are the trade-offs or considerations?

CRITICAL RULES:
- Use ONLY the numbers provided above. DO NOT calculate, modify, or invent any new numbers.
- Explain the What-If results, do not perform financial calculations.
- Keep the language clear, simple, and conversational.
- Use Indian Rupees (₹) as the currency.
- Be practical and realistic in your assessment.
- Keep the narration to 300-400 words.

Please provide the What-If scenario narration now:"""
    
    return prompt


def create_system_message() -> str:
    """
    Create the system message for the What-If narration task.
    
    Returns:
        System message string.
    """
    return """You are a friendly and practical financial advisor who helps customers understand 
"What-If" scenarios. Your role is to explain how changes in their situation would impact their 
financial plans. You present the analysis clearly, explaining cause and effect, and help them 
understand whether a potential change would help or hurt their progress toward their goals. 
You never invent numbers or perform calculations - you only explain and interpret the analysis 
results provided to you. You are encouraging but realistic, helping customers make informed 
decisions about potential life changes."""
