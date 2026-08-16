"""
Example usage of the plan comparator module.

This demonstrates how to integrate Member 2's plan generation
with Member 4's plan comparison.
"""

from dotenv import load_dotenv
import pandas as pd

from app.core.plan_generator import generate_plans
from app.genai.comparator import compare_plans, compare_plans_structured

# Load environment variables (for GROQ_API_KEY)
load_dotenv()


def example_basic_comparison():
    """Example: Basic comparison of three plans."""
    
    print("Example 1: Basic Plan Comparison")
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
    
    # Generate all three plans
    plans = generate_plans(customer_profile, "Moderate", goal, historical_data)
    
    # Compare them
    comparison = compare_plans(plans)
    
    print(f"\nGenerated comparison for {len(plans)} plans")
    print(f"\nComparison:\n{comparison}")
    print()


def example_structured_comparison():
    """Example: Structured comparison with metadata."""
    
    print("\nExample 2: Structured Comparison")
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
    plans = generate_plans(customer_profile, "Aggressive", goal, historical_data)
    
    # Get structured comparison
    result = compare_plans_structured(plans)
    
    print(f"\nStructured result contains:")
    print(f"  - plans: {len(result['plans'])} plans")
    print(f"  - plan_names: {result['plan_names']}")
    print(f"  - risk_levels: {result['risk_levels']}")
    print(f"  - comparison: {len(result['comparison'])} characters")
    print()
    print(f"Comparison text:\n{result['comparison']}")
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
    
    # Compare with lower temperature (more focused) and more tokens (longer response)
    comparison = compare_plans(
        plans,
        temperature=0.5,  # More focused, less creative
        max_tokens=1000   # Longer, more detailed response
    )
    
    print(f"\nParameters: temperature=0.5, max_tokens=1000")
    print(f"\nComparison:\n{comparison}")
    print()


def example_api_integration():
    """Example: How an API route might use the comparator."""
    
    print("\nExample 4: API Integration Pattern")
    print("=" * 80)
    
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
        
        # Generate comparison
        comparison = compare_plans(plans, temperature=0.7, max_tokens=800)
        
        # Build API response
        response = {
            "status": "success",
            "plans": plans,
            "comparison": comparison,
            "plan_count": len(plans),
        }
        
        print("API Response structure:")
        print(f"  Status: {response['status']}")
        print(f"  Number of plans: {response['plan_count']}")
        print(f"  Comparison length: {len(response['comparison'])} chars")
        print(f"\nFirst 200 chars of comparison:")
        print(f"  {response['comparison'][:200]}...")
        
    except ValueError as e:
        print(f"Validation error: {e}")
    except Exception as e:
        print(f"Error: {e}")


def example_combined_with_explainer():
    """Example: Use both explainer and comparator together."""
    
    print("\nExample 5: Combined Explainer + Comparator")
    print("=" * 80)
    
    from app.genai.explainer import explain_plan
    
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
    
    # First, show comparison of all three
    comparison = compare_plans(plans)
    print("\n1. COMPARISON OF ALL THREE PLANS:")
    print("-" * 80)
    print(comparison)
    print()
    
    # Then, show detailed explanation of recommended plan (e.g., Balanced)
    recommended_plan = plans[1]  # Balanced
    explanation = explain_plan(recommended_plan)
    print(f"\n2. DETAILED EXPLANATION OF {recommended_plan['plan_name']} PLAN:")
    print("-" * 80)
    print(explanation)
    print()


if __name__ == "__main__":
    # Run examples (comment out as needed)
    
    # Basic comparison
    # example_basic_comparison()
    
    # Structured comparison
    # example_structured_comparison()
    
    # Custom parameters
    # example_custom_parameters()
    
    # API integration pattern (doesn't call LLM, just shows structure)
    example_api_integration()
    
    # Combined explainer + comparator
    # example_combined_with_explainer()
