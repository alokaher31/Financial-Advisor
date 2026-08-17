"""
Financial plan explainer module.
Generates natural language explanations of financial plans using the LLM.
"""

from typing import Dict, Any, Optional

from .llm_client import generate_llm_response
from .prompts.plan_explanation_prompt import (
    create_plan_explanation_prompt,
    create_system_message,
)


def explain_plan(
    plan: Dict[str, Any],
    temperature: float = 0.7,
    max_tokens: int = 600,
) -> str:
    """
    Generate a natural language explanation of a financial plan.
    
    This function takes a plan dictionary (as returned by generate_plans())
    and uses the LLM to create a clear, customer-friendly explanation.
    
    Args:
        plan: Dictionary containing plan details with keys:
            - plan_name: str (e.g., "Conservative", "Balanced", "Growth")
            - allocation: dict (e.g., {"Equity": 20, "Debt": 50, ...})
            - blended_expected_return: float (percentage)
            - projected_corpus: float (future value)
            - gap_vs_target: float (positive = surplus, negative = shortfall)
            - required_monthly_investment: float (monthly amount)
            - risk_level: str (e.g., "Conservative", "Moderate", "Aggressive")
        temperature: LLM sampling temperature (0.0-2.0). Lower = more focused.
        max_tokens: Maximum tokens in the LLM response.
    
    Returns:
        A natural language explanation string of the plan.
        
    Raises:
        ValueError: If the plan is missing required fields.
        Exception: If the LLM call fails after retries.
    
    Example:
        >>> plan = {
        ...     "plan_name": "Balanced",
        ...     "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        ...     "blended_expected_return": 9.9,
        ...     "projected_corpus": 3456789.01,
        ...     "gap_vs_target": -1543210.99,
        ...     "required_monthly_investment": 42000.50,
        ...     "risk_level": "Moderate"
        ... }
        >>> explanation = explain_plan(plan)
        >>> print(explanation)
        The Balanced plan offers a Moderate risk approach...
    """
    
    # Validate required fields
    required_fields = [
        "plan_name",
        "allocation",
        "blended_expected_return",
        "projected_corpus",
        "gap_vs_target",
        "required_monthly_investment",
        "risk_level",
    ]
    
    missing_fields = [field for field in required_fields if field not in plan]
    if missing_fields:
        raise ValueError(
            f"Plan is missing required fields: {', '.join(missing_fields)}"
        )
    
    # Validate allocation is a dict
    if not isinstance(plan["allocation"], dict):
        raise ValueError("Plan allocation must be a dictionary")
    
    # Create the prompt
    user_prompt = create_plan_explanation_prompt(plan)
    system_message = create_system_message()
    
    # Call the LLM
    explanation = generate_llm_response(
        prompt=user_prompt,
        system_message=system_message,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return explanation


def explain_multiple_plans(
    plans: list[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 600,
) -> list[str]:
    """
    Generate explanations for multiple plans.
    
    This is a convenience function that calls explain_plan() for each plan
    in the list.
    
    Args:
        plans: List of plan dictionaries (e.g., from generate_plans())
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens per explanation
    
    Returns:
        List of explanation strings, one for each plan.
        
    Example:
        >>> plans = generate_plans(profile, risk, goal, data)
        >>> explanations = explain_multiple_plans(plans)
        >>> for plan, explanation in zip(plans, explanations):
        ...     print(f"{plan['plan_name']}:")
        ...     print(explanation)
        ...     print()
    """
    explanations = []
    for plan in plans:
        explanation = explain_plan(plan, temperature=temperature, max_tokens=max_tokens)
        explanations.append(explanation)
    return explanations
