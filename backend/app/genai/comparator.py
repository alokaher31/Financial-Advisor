"""
Financial plan comparator module.
Generates side-by-side comparisons of three financial plans using the LLM.
"""

from typing import Dict, Any, List

from .llm_client import generate_llm_response
from .prompts.plan_comparison_prompt import (
    create_plan_comparison_prompt,
    create_system_message,
)


def compare_plans(
    plans: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 800,
) -> str:
    """
    Generate a natural language comparison of three financial plans.
    
    This function takes three plan dictionaries (as returned by generate_plans())
    and uses the LLM to create a clear, comprehensive comparison explaining the
    differences, trade-offs, and suitability of each plan.
    
    Args:
        plans: List of exactly 3 plan dictionaries (Conservative, Balanced, Growth).
               Each plan must contain:
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
        A natural language comparison string of the three plans.
        
    Raises:
        ValueError: If not exactly 3 plans provided or if plans are missing required fields.
        Exception: If the LLM call fails after retries.
    
    Example:
        >>> plans = generate_plans(profile, risk, goal, data)
        >>> comparison = compare_plans(plans)
        >>> print(comparison)
        The three plans offer different approaches to reaching your goal...
        
        Conservative Plan (Conservative Risk):
        - Lower risk with 20% in equity...
        
        Balanced Plan (Moderate Risk):
        - Balanced approach with 50% in equity...
        
        Growth Plan (Aggressive Risk):
        - Higher growth potential with 70% in equity...
    """
    
    # Validate we have exactly 3 plans
    if not isinstance(plans, list):
        raise ValueError("plans must be a list")
    
    if len(plans) != 3:
        raise ValueError(f"Expected exactly 3 plans, got {len(plans)}")
    
    # Validate required fields for each plan
    required_fields = [
        "plan_name",
        "allocation",
        "blended_expected_return",
        "projected_corpus",
        "gap_vs_target",
        "required_monthly_investment",
        "risk_level",
    ]
    
    for i, plan in enumerate(plans):
        if not isinstance(plan, dict):
            raise ValueError(f"Plan {i+1} must be a dictionary")
        
        missing_fields = [field for field in required_fields if field not in plan]
        if missing_fields:
            raise ValueError(
                f"Plan {i+1} ({plan.get('plan_name', 'Unknown')}) is missing required fields: "
                f"{', '.join(missing_fields)}"
            )
        
        # Validate allocation is a dict
        if not isinstance(plan["allocation"], dict):
            raise ValueError(
                f"Plan {i+1} ({plan.get('plan_name', 'Unknown')}) allocation must be a dictionary"
            )
    
    # Create the prompt
    user_prompt = create_plan_comparison_prompt(plans)
    system_message = create_system_message()
    
    # Call the LLM
    comparison = generate_llm_response(
        prompt=user_prompt,
        system_message=system_message,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return comparison


def compare_plans_structured(
    plans: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 800,
) -> Dict[str, Any]:
    """
    Generate a structured comparison with both plans and comparison text.
    
    This is a convenience function that returns both the original plan data
    and the comparison text in a single structured response.
    
    Args:
        plans: List of exactly 3 plan dictionaries
        temperature: LLM sampling temperature
        max_tokens: Maximum tokens in response
    
    Returns:
        Dictionary with:
            - plans: The original 3 plan dictionaries
            - comparison: The natural language comparison text
            - plan_names: List of plan names for quick reference
    
    Example:
        >>> result = compare_plans_structured(plans)
        >>> print(result['comparison'])
        >>> print(result['plan_names'])  # ['Conservative', 'Balanced', 'Growth']
    """
    
    comparison_text = compare_plans(plans, temperature=temperature, max_tokens=max_tokens)
    
    return {
        "plans": plans,
        "comparison": comparison_text,
        "plan_names": [plan["plan_name"] for plan in plans],
        "risk_levels": [plan["risk_level"] for plan in plans],
    }
