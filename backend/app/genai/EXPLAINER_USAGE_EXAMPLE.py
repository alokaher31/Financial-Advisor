"""
Example usage of the plan explainer module.

This demonstrates how to integrate Member 2's plan generation
with Member 4's plan explanation.
"""

from dotenv import load_dotenv
import pandas as pd

from app.core.plan_generator import generate_plans
from app.genai.explainer import explain_plan, explain_multiple_plans

# Load environment variables (for GROQ_API_KEY)
load_dotenv()


def example_single_plan_explanation():
    """Example: Explain a single plan."""
    
    print("Example 1: Single Plan Explanation")
    print("=" * 80)
    
    # Setup data
    historical_data = pd.DataFrame({
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.0, 9.0, 8.0, 5.5],
        "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
    })
    
    customer_profile = {
        "monthly_income": 100_000,
        "monthly_expenses": 60_000
    }
    
    goal = {
        "target_amount": 5_000_000,
        "current_amount": 200_000,
        "time_horizon_years": 5,
    }
    
    # Generate plans
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    
    # Explain the Balanced plan
    balanced_plan = plans[1]  # Index 1 is Balanced
    explanation = explain_plan(balanced_plan)
    
    print(f"\nPlan: {balanced_plan['plan_name']}")
    print(f"Risk Level: {balanced_plan['risk_level']}")
    print(f"\nExplanation:\n{explanation}")
    print()


def example_all_plans_explanation():
    """Example: Explain all three plans."""
    
    print("\nExample 2: All Plans Explanation")
    print("=" * 80)
    
    # Setup data
    historical_data = pd.DataFrame({
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.0, 9.0, 8.0, 5.5],
        "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
    })
    
    customer_profile = {
        "monthly_income": 150_000,
        "monthly_expenses": 80_000
    }
    
    goal = {
        "target_amount": 10_000_000,
        "current_amount": 500_000,
        "time_horizon_years": 10,
    }
    
    # Generate plans
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    
    # Explain all plans
    explanations = explain_multiple_plans(plans, temperature=0.7, max_tokens=600)
    
    for plan, explanation in zip(plans, explanations):
        print(f"\n{plan['plan_name']} Plan ({plan['risk_level']} Risk)")
        print("-" * 80)
        print(explanation)
        print()


def example_custom_parameters():
    """Example: Use custom temperature and max_tokens."""
    
    print("\nExample 3: Custom LLM Parameters")
    print("=" * 80)
    
    # Setup data
    historical_data = pd.DataFrame({
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.0, 9.0, 8.0, 5.5],
        "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
    })
    
    customer_profile = {
        "monthly_income": 80_000,
        "monthly_expenses": 50_000
    }
    
    goal = {
        "target_amount": 3_000_000,
        "current_amount": 100_000,
        "time_horizon_years": 7,
    }
    
    # Generate plans
    plans = generate_plans(customer_profile, "Conservative", goal, historical_data)
    
    # Explain with lower temperature (more focused) and fewer tokens
    conservative_plan = plans[0]
    explanation = explain_plan(
        conservative_plan,
        temperature=0.3,  # More focused, less creative
        max_tokens=400    # Shorter response
    )
    
    print(f"\nPlan: {conservative_plan['plan_name']}")
    print(f"Parameters: temperature=0.3, max_tokens=400")
    print(f"\nExplanation:\n{explanation}")
    print()


def example_api_integration():
    """Example: How an API route might use this."""
    
    print("\nExample 4: API Integration Pattern")
    print("=" * 80)
    
    # This is how a FastAPI route might use the explainer
    
    # Assume we received these from the API request
    customer_profile = {
        "monthly_income": 120_000,
        "monthly_expenses": 70_000
    }
    
    goal = {
        "target_amount": 8_000_000,
        "current_amount": 300_000,
        "time_horizon_years": 8,
    }
    
    risk_category = "Moderate"
    
    # Load historical data (in real API, this might come from database)
    historical_data = pd.DataFrame({
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.0, 9.0, 8.0, 5.5],
        "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
    })
    
    try:
        # Generate plans
        plans = generate_plans(
            customer_profile,
            risk_category,
            goal,
            historical_data
        )
        
        # Generate explanations
        explanations = explain_multiple_plans(plans)
        
        # Build API response
        response = {
            "status": "success",
            "plans": [
                {
                    **plan,
                    "explanation": explanation
                }
                for plan, explanation in zip(plans, explanations)
            ]
        }
        
        print("API Response structure:")
        print(f"  Status: {response['status']}")
        print(f"  Number of plans: {len(response['plans'])}")
        for i, plan_with_explanation in enumerate(response['plans']):
            print(f"\n  Plan {i+1}: {plan_with_explanation['plan_name']}")
            print(f"    Has explanation: {bool(plan_with_explanation.get('explanation'))}")
            print(f"    Explanation length: {len(plan_with_explanation['explanation'])} chars")
        
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run examples (comment out as needed)
    
    # Single plan
    # example_single_plan_explanation()
    
    # All plans
    # example_all_plans_explanation()
    
    # Custom parameters
    # example_custom_parameters()
    
    # API integration pattern (doesn't call LLM, just shows structure)
    example_api_integration()
