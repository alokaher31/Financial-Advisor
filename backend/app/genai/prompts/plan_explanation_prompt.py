"""
Prompt template for explaining a financial plan to a customer.
"""


def create_plan_explanation_prompt(plan: dict) -> str:
    """
    Create a prompt for the LLM to explain a financial plan in simple language.
    
    Args:
        plan: Dictionary containing the plan details with keys:
            - plan_name: str (e.g., "Conservative", "Balanced", "Growth")
            - allocation: dict (e.g., {"Equity": 20, "Debt": 50, ...})
            - blended_expected_return: float (percentage)
            - projected_corpus: float (amount in currency)
            - gap_vs_target: float (positive = surplus, negative = shortfall)
            - required_monthly_investment: float (monthly amount needed)
            - risk_level: str (e.g., "Conservative", "Moderate", "Aggressive")
    
    Returns:
        A formatted prompt string for the LLM.
    """
    
    # Format allocation for readability
    allocation_str = ", ".join(
        f"{asset}: {percentage}%" 
        for asset, percentage in plan["allocation"].items()
    )
    
    # Determine if there's a gap or surplus
    gap = plan["gap_vs_target"]
    if gap < 0:
        gap_status = "SHORTFALL"
        gap_amount = abs(gap)
    elif gap > 0:
        gap_status = "SURPLUS"
        gap_amount = gap
    else:
        gap_status = "EXACT MATCH"
        gap_amount = 0
    
    prompt = f"""You are a financial advisor explaining a personalized investment plan to a customer. 
Your goal is to help them understand their financial plan in clear, simple language.

PLAN DETAILS:
- Plan Name: {plan['plan_name']}
- Risk Level: {plan['risk_level']}
- Asset Allocation: {allocation_str}
- Blended Expected Return: {plan['blended_expected_return']}% per year
- Projected Corpus (Future Value): ₹{plan['projected_corpus']:,.2f}
- Gap vs Target: {gap_status} of ₹{gap_amount:,.2f}
- Required Monthly Investment: ₹{plan['required_monthly_investment']:,.2f}

INSTRUCTIONS:
1. Start with a brief overview of the {plan['plan_name']} plan and its {plan['risk_level']} risk level.
2. Explain the asset allocation strategy - what it means and why it's structured this way.
3. Explain what the {plan['blended_expected_return']}% expected return means.
4. Explain the projected corpus (₹{plan['projected_corpus']:,.2f}) - this is what the customer's investments will grow to.
5. Clearly explain the gap situation:
   - If SHORTFALL: explain they need ₹{gap_amount:,.2f} more to reach their goal
   - If SURPLUS: explain they will exceed their goal by ₹{gap_amount:,.2f}
   - If EXACT MATCH: explain they will exactly meet their goal
6. Explain the required monthly investment (₹{plan['required_monthly_investment']:,.2f}) - what they need to invest each month.
7. End with a brief summary of whether this plan helps them meet their financial goals.

IMPORTANT RULES:
- Use ONLY the numbers provided above. DO NOT calculate or invent any new numbers.
- Explain the calculations conceptually, but do not perform mathematical operations.
- Keep the language simple and conversational, as if speaking to someone without financial expertise.
- Use Indian Rupees (₹) as the currency.
- Be encouraging but realistic about the plan's potential.
- Keep the explanation to 250-350 words.

Please provide the explanation now:"""
    
    return prompt


def create_system_message() -> str:
    """
    Create the system message for the plan explanation task.
    
    Returns:
        System message string.
    """
    return """You are a friendly and knowledgeable financial advisor. 
Your role is to explain financial plans in simple, clear language that anyone can understand. 
You never invent numbers or perform calculations - you only explain the numbers and concepts provided to you.
You are patient, encouraging, and focused on helping customers understand their financial situation."""
