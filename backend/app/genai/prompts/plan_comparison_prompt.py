"""
Prompt template for comparing three financial plans side-by-side.
"""


def create_plan_comparison_prompt(plans: list[dict]) -> str:
    """
    Create a prompt for the LLM to compare three financial plans.
    
    Args:
        plans: List of 3 plan dictionaries (Conservative, Balanced, Growth) from generate_plans().
               Each plan contains:
                   - plan_name: str
                   - allocation: dict (e.g., {"Equity": 20, "Debt": 50, ...})
                   - blended_expected_return: float
                   - projected_corpus: float
                   - gap_vs_target: float (positive = surplus, negative = shortfall)
                   - required_monthly_investment: float
                   - risk_level: str
    
    Returns:
        A formatted prompt string for the LLM to compare the three plans.
    """
    
    if len(plans) != 3:
        raise ValueError(f"Expected exactly 3 plans, got {len(plans)}")
    
    # Extract the three plans (should be Conservative, Balanced, Growth)
    plan1, plan2, plan3 = plans
    
    def format_allocation(allocation: dict) -> str:
        """Format allocation dict as readable string."""
        return ", ".join(f"{asset}: {pct}%" for asset, pct in allocation.items())
    
    def format_gap(gap: float) -> tuple[str, float]:
        """Format gap as (status, amount) tuple."""
        if gap < 0:
            return "SHORTFALL", abs(gap)
        elif gap > 0:
            return "SURPLUS", gap
        else:
            return "EXACT MATCH", 0.0
    
    # Format gap information for each plan
    gap1_status, gap1_amount = format_gap(plan1["gap_vs_target"])
    gap2_status, gap2_amount = format_gap(plan2["gap_vs_target"])
    gap3_status, gap3_amount = format_gap(plan3["gap_vs_target"])
    
    prompt = f"""You are a financial advisor helping a customer compare three different investment plan options. 
Your goal is to explain the differences between the plans in clear, simple language so they can make an informed decision.

PLAN COMPARISON:

═══════════════════════════════════════════════════════════════════════════════
PLAN 1: {plan1['plan_name']}
═══════════════════════════════════════════════════════════════════════════════
Risk Level: {plan1['risk_level']}
Asset Allocation: {format_allocation(plan1['allocation'])}
Expected Annual Return: {plan1['blended_expected_return']}%
Projected Future Value: ₹{plan1['projected_corpus']:,.2f}
Gap vs Target: {gap1_status} of ₹{gap1_amount:,.2f}
Required Monthly Investment: ₹{plan1['required_monthly_investment']:,.2f}

═══════════════════════════════════════════════════════════════════════════════
PLAN 2: {plan2['plan_name']}
═══════════════════════════════════════════════════════════════════════════════
Risk Level: {plan2['risk_level']}
Asset Allocation: {format_allocation(plan2['allocation'])}
Expected Annual Return: {plan2['blended_expected_return']}%
Projected Future Value: ₹{plan2['projected_corpus']:,.2f}
Gap vs Target: {gap2_status} of ₹{gap2_amount:,.2f}
Required Monthly Investment: ₹{plan2['required_monthly_investment']:,.2f}

═══════════════════════════════════════════════════════════════════════════════
PLAN 3: {plan3['plan_name']}
═══════════════════════════════════════════════════════════════════════════════
Risk Level: {plan3['risk_level']}
Asset Allocation: {format_allocation(plan3['allocation'])}
Expected Annual Return: {plan3['blended_expected_return']}%
Projected Future Value: ₹{plan3['projected_corpus']:,.2f}
Gap vs Target: {gap3_status} of ₹{gap3_amount:,.2f}
Required Monthly Investment: ₹{plan3['required_monthly_investment']:,.2f}

═══════════════════════════════════════════════════════════════════════════════

INSTRUCTIONS:

1. **Risk Level Comparison**
   Compare the three risk levels ({plan1['risk_level']}, {plan2['risk_level']}, {plan3['risk_level']}) 
   and explain what each means for the customer.

2. **Asset Allocation Differences**
   Explain how the asset mix differs across the three plans:
   - How much equity exposure changes from {plan1['plan_name']} to {plan3['plan_name']}
   - How debt, gold, real estate, and cash allocations shift
   - What these allocation differences mean for risk and potential returns

3. **Expected Return Comparison**
   Compare the expected returns ({plan1['blended_expected_return']}%, {plan2['blended_expected_return']}%, {plan3['blended_expected_return']}%)
   and explain why they differ based on the asset allocations.

4. **Projected Corpus Comparison**
   Compare the projected future values:
   - {plan1['plan_name']}: ₹{plan1['projected_corpus']:,.2f}
   - {plan2['plan_name']}: ₹{plan2['projected_corpus']:,.2f}
   - {plan3['plan_name']}: ₹{plan3['projected_corpus']:,.2f}
   Explain which plan grows the money the most and why.

5. **Gap Analysis Comparison**
   Compare how each plan performs against the target:
   - {plan1['plan_name']}: {gap1_status} of ₹{gap1_amount:,.2f}
   - {plan2['plan_name']}: {gap2_status} of ₹{gap2_amount:,.2f}
   - {plan3['plan_name']}: {gap3_status} of ₹{gap3_amount:,.2f}
   Explain which plan gets closest to the target goal.

6. **Required Investment Comparison**
   Compare the monthly investment requirements:
   - {plan1['plan_name']}: ₹{plan1['required_monthly_investment']:,.2f}
   - {plan2['plan_name']}: ₹{plan2['required_monthly_investment']:,.2f}
   - {plan3['plan_name']}: ₹{plan3['required_monthly_investment']:,.2f}
   Explain why the requirements differ.

7. **Trade-offs Summary**
   Clearly explain the key trade-offs:
   - What you gain by moving from {plan1['plan_name']} to {plan2['plan_name']} to {plan3['plan_name']}
   - What you risk by choosing higher-growth plans
   - Which plan might be suitable for different customer situations

8. **Recommendation Guidance**
   End with guidance on how to choose between the three plans based on:
   - Risk tolerance
   - Time horizon
   - Financial goals
   - Monthly investment capacity

CRITICAL RULES:
- Use ONLY the numbers provided above. DO NOT calculate, modify, or invent any new numbers.
- Explain the differences conceptually. Do not perform mathematical operations.
- Keep the language simple and conversational, as if speaking to someone without financial expertise.
- Use Indian Rupees (₹) as the currency.
- Be objective - don't push one plan over another, explain trade-offs neutrally.
- Keep the comparison to 400-500 words.

Please provide the comparison now:"""
    
    return prompt


def create_system_message() -> str:
    """
    Create the system message for the plan comparison task.
    
    Returns:
        System message string.
    """
    return """You are a friendly and knowledgeable financial advisor who specializes in helping customers 
understand their investment options. Your role is to compare different financial plans side-by-side 
in clear, simple language that anyone can understand. You present information objectively, explaining 
the trade-offs without pushing any particular option. You never invent numbers or perform calculations - 
you only explain and compare the numbers and concepts provided to you. You are patient, thorough, and 
focused on helping customers make informed decisions."""
