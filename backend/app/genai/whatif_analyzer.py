"""
What-If scenario analyzer and narrator module.
Performs What-If analysis by comparing base and adjusted financial plans,
then generates natural language narration of the results.
"""

from typing import Dict, Any, Optional
import pandas as pd

from app.core.plan_generator import generate_plans
from .llm_client import generate_llm_response
from .prompts.whatif_narration_prompt import (
    create_whatif_narration_prompt,
    create_system_message,
)


def calculate_whatif_scenario(
    customer_profile: Dict[str, Any],
    goal: Dict[str, Any],
    risk_category: str,
    historical_data: pd.DataFrame,
    adjustment_parameter: str,
    adjusted_value: float,
    plan_name: str = "Balanced",
    scenario_type: str = None,
    original_scenario_amount: float = None,
) -> Dict[str, Any]:
    """
    Calculate a What-If scenario by comparing base and adjusted plans.
    
    This function:
    1. Generates base plans with original inputs
    2. Adjusts the specified parameter
    3. Generates adjusted plans with the new value
    4. Compares the two to show impact
    
    Args:
        customer_profile: Dict with 'monthly_income' and 'monthly_expenses'
        goal: Dict with 'target_amount', 'current_amount', 'time_horizon_years'
        risk_category: Risk category (Conservative, Moderate, or Aggressive)
        historical_data: Historical returns DataFrame
        adjustment_parameter: Parameter to adjust ('monthly_income', 'monthly_expenses', 
                             'time_horizon_years', 'current_amount', 'target_amount')
        adjusted_value: New value for the parameter
        plan_name: Which plan to compare (Conservative, Balanced, or Growth). Default: Balanced
        scenario_type: Original scenario type (e.g., 'extra_monthly_investment')
        original_scenario_amount: Original amount from the user request
    
    Returns:
        Dictionary with What-If analysis results containing:
            - scenario_name
            - scenario_type
            - adjustments
            - base_plan
            - adjusted_plan
            - impact
    
    Raises:
        ValueError: If adjustment_parameter is invalid or plan_name not found
    
    Example:
        >>> result = calculate_whatif_scenario(
        ...     customer_profile={'monthly_income': 100000, 'monthly_expenses': 60000},
        ...     goal={'target_amount': 5000000, 'current_amount': 200000, 'time_horizon_years': 5},
        ...     risk_category='Moderate',
        ...     historical_data=data,
        ...     adjustment_parameter='monthly_expenses',
        ...     adjusted_value=50000,
        ...     plan_name='Balanced',
        ...     scenario_type='extra_monthly_investment',
        ...     original_scenario_amount=10000
        ... )
    """
    
    # Validate adjustment parameter
    valid_parameters = {
        'monthly_income', 'monthly_expenses', 'time_horizon_years', 
        'current_amount', 'target_amount'
    }
    if adjustment_parameter not in valid_parameters:
        raise ValueError(
            f"adjustment_parameter must be one of {valid_parameters}, got '{adjustment_parameter}'"
        )
    
    # Validate plan name
    valid_plan_names = {'Conservative', 'Balanced', 'Growth'}
    if plan_name not in valid_plan_names:
        raise ValueError(
            f"plan_name must be one of {valid_plan_names}, got '{plan_name}'"
        )
    
    # Get original value
    if adjustment_parameter in ['monthly_income', 'monthly_expenses']:
        original_value = customer_profile[adjustment_parameter]
    else:  # goal parameters
        original_value = goal[adjustment_parameter]
    
    # Generate base plans
    base_plans = generate_plans(customer_profile, risk_category, goal, historical_data)
    
    # Find the specified plan in base plans
    base_plan = None
    for plan in base_plans:
        if plan['plan_name'] == plan_name:
            base_plan = plan
            break
    
    if base_plan is None:
        raise ValueError(f"Plan '{plan_name}' not found in base plans")
    
    # Create adjusted inputs
    adjusted_profile = dict(customer_profile)
    adjusted_goal = dict(goal)
    
    if adjustment_parameter in ['monthly_income', 'monthly_expenses']:
        adjusted_profile[adjustment_parameter] = adjusted_value
    else:
        adjusted_goal[adjustment_parameter] = adjusted_value
    
    # Generate adjusted plans
    adjusted_plans = generate_plans(adjusted_profile, risk_category, adjusted_goal, historical_data)
    
    # Find the same plan in adjusted plans
    adjusted_plan = None
    for plan in adjusted_plans:
        if plan['plan_name'] == plan_name:
            adjusted_plan = plan
            break
    
    if adjusted_plan is None:
        raise ValueError(f"Plan '{plan_name}' not found in adjusted plans")
    
    # Calculate impact
    corpus_change = adjusted_plan['projected_corpus'] - base_plan['projected_corpus']
    gap_change = adjusted_plan['gap_vs_target'] - base_plan['gap_vs_target']
    investment_change = adjusted_plan['required_monthly_investment'] - base_plan['required_monthly_investment']
    
    # Determine if gap improved (moved closer to zero or became positive)
    gap_improvement = gap_change > 0
    
    # Create scenario name and type based on the original request
    if scenario_type == "extra_monthly_investment" and original_scenario_amount:
        scenario_name = f"Increase Monthly Investment by ₹{original_scenario_amount:,.2f}"
        scenario_type_final = "monthly_investment_increase"
        # For display purposes, show the actual contribution change
        parameter_display = "Monthly Investment"
        original_surplus = customer_profile['monthly_income'] - customer_profile['monthly_expenses']
        adjusted_surplus = customer_profile['monthly_income'] - adjusted_value
        change = adjusted_surplus - original_surplus
    else:
        # Fallback to the old logic for other scenarios
        change = adjusted_value - original_value
        parameter_display = adjustment_parameter.replace('_', ' ').title()
        
        if change > 0:
            scenario_name = f"Increase {parameter_display} by ₹{abs(change):,.2f}"
            scenario_type_final = f"{adjustment_parameter}_increase"
        elif change < 0:
            scenario_name = f"Reduce {parameter_display} by ₹{abs(change):,.2f}"
            scenario_type_final = f"{adjustment_parameter}_decrease"
        else:
            scenario_name = f"No change in {parameter_display}"
            scenario_type_final = f"{adjustment_parameter}_no_change"
    
    # Build result
    return {
        "scenario_name": scenario_name,
        "scenario_type": scenario_type_final,
        "adjustments": {
            "parameter": parameter_display.lower().replace(' ', '_'),
            "original_value": float(original_value),
            "adjusted_value": float(adjusted_value),
            "change": float(change),
        },
        "base_plan": {
            "plan_name": base_plan['plan_name'],
            "projected_corpus": float(base_plan['projected_corpus']),
            "gap_vs_target": float(base_plan['gap_vs_target']),
            "required_monthly_investment": float(base_plan['required_monthly_investment']),
            "blended_expected_return": float(base_plan['blended_expected_return']),
            "risk_level": base_plan['risk_level'],
            "allocation": dict(base_plan['allocation']),
        },
        "adjusted_plan": {
            "plan_name": adjusted_plan['plan_name'],
            "projected_corpus": float(adjusted_plan['projected_corpus']),
            "gap_vs_target": float(adjusted_plan['gap_vs_target']),
            "required_monthly_investment": float(adjusted_plan['required_monthly_investment']),
            "blended_expected_return": float(adjusted_plan['blended_expected_return']),
            "risk_level": adjusted_plan['risk_level'],
            "allocation": dict(adjusted_plan['allocation']),
        },
        "impact": {
            "corpus_change": float(corpus_change),
            "gap_change": float(gap_change),
            "investment_change": float(investment_change),
            "gap_improvement": bool(gap_improvement),
        },
    }


def narrate_whatif_scenario(
    whatif_result: Dict[str, Any],
    temperature: float = 0.7,
    max_tokens: int = 600,
) -> str:
    """
    Generate a natural language narration of a What-If scenario analysis.
    
    This function takes a What-If analysis result (from calculate_whatif_scenario())
    and uses the LLM to create a clear, customer-friendly explanation.
    
    Args:
        whatif_result: Dictionary from calculate_whatif_scenario() containing
                      scenario details, base plan, adjusted plan, and impact
        temperature: LLM sampling temperature (0.0-2.0). Lower = more focused.
        max_tokens: Maximum tokens in the LLM response.
    
    Returns:
        A natural language narration string explaining the What-If scenario.
        
    Raises:
        ValueError: If whatif_result is missing required fields.
        Exception: If the LLM call fails after retries.
    
    Example:
        >>> whatif_result = calculate_whatif_scenario(...)
        >>> narration = narrate_whatif_scenario(whatif_result)
        >>> print(narration)
        Let's explore what would happen if you reduced your monthly expenses by ₹10,000...
    """
    
    # Validate required fields
    required_fields = [
        'scenario_name', 'scenario_type', 'adjustments',
        'base_plan', 'adjusted_plan', 'impact'
    ]
    
    missing_fields = [field for field in required_fields if field not in whatif_result]
    if missing_fields:
        raise ValueError(
            f"whatif_result is missing required fields: {', '.join(missing_fields)}"
        )
    
    # Create the prompt
    user_prompt = create_whatif_narration_prompt(whatif_result)
    system_message = create_system_message()
    
    # Call the LLM
    narration = generate_llm_response(
        prompt=user_prompt,
        system_message=system_message,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    return narration


def analyze_and_narrate_whatif(
    customer_profile: Dict[str, Any],
    goal: Dict[str, Any],
    risk_category: str,
    historical_data: pd.DataFrame,
    adjustment_parameter: str,
    adjusted_value: float,
    plan_name: str = "Balanced",
    temperature: float = 0.7,
    max_tokens: int = 600,
) -> Dict[str, Any]:
    """
    Perform What-If analysis and generate narration in one call.
    
    This is a convenience function that combines calculate_whatif_scenario()
    and narrate_whatif_scenario().
    
    Args:
        (Same as calculate_whatif_scenario, plus temperature and max_tokens)
    
    Returns:
        Dictionary containing both the analysis and narration:
            - All fields from calculate_whatif_scenario()
            - narration: The natural language explanation
    
    Example:
        >>> result = analyze_and_narrate_whatif(
        ...     customer_profile={'monthly_income': 100000, 'monthly_expenses': 60000},
        ...     goal={'target_amount': 5000000, 'current_amount': 200000, 'time_horizon_years': 5},
        ...     risk_category='Moderate',
        ...     historical_data=data,
        ...     adjustment_parameter='monthly_expenses',
        ...     adjusted_value=50000
        ... )
        >>> print(result['narration'])
    """
    
    # Calculate What-If scenario
    whatif_result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category=risk_category,
        historical_data=historical_data,
        adjustment_parameter=adjustment_parameter,
        adjusted_value=adjusted_value,
        plan_name=plan_name,
    )
    
    # Generate narration
    narration = narrate_whatif_scenario(
        whatif_result=whatif_result,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    
    # Combine results
    result = dict(whatif_result)
    result['narration'] = narration
    
    return result
