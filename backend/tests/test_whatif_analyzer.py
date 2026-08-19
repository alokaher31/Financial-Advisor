"""
Tests for the What-If scenario analyzer and narrator module.
"""

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from app.genai.whatif_analyzer import (
    calculate_whatif_scenario,
    narrate_whatif_scenario,
    analyze_and_narrate_whatif,
)
from app.genai.prompts.whatif_narration_prompt import (
    create_whatif_narration_prompt,
    create_system_message,
)


@pytest.fixture
def historical_data():
    """Sample historical returns data."""
    return pd.DataFrame({
        "asset_category": ["Equity", "Debt", "Gold", "Real_Estate", "Cash"],
        "avg_annual_return": [12.0, 7.0, 9.0, 8.0, 5.5],
        "volatility": [18.0, 4.0, 12.0, 8.0, 1.0],
    })


@pytest.fixture
def customer_profile():
    """Sample customer profile."""
    return {
        "monthly_income": 100_000,
        "monthly_expenses": 60_000,
    }


@pytest.fixture
def goal():
    """Sample financial goal."""
    return {
        "target_amount": 5_000_000,
        "current_amount": 200_000,
        "time_horizon_years": 5,
    }


@pytest.fixture
def sample_whatif_result():
    """Sample What-If analysis result."""
    return {
        "scenario_name": "Reduce Monthly Expenses by ₹10,000.00",
        "scenario_type": "monthly_expenses_decrease",
        "adjustments": {
            "parameter": "monthly_expenses",
            "original_value": 60000.0,
            "adjusted_value": 50000.0,
            "change": -10000.0,
        },
        "base_plan": {
            "plan_name": "Balanced",
            "projected_corpus": 3416744.29,
            "gap_vs_target": -1583255.71,
            "required_monthly_investment": 60499.80,
            "blended_expected_return": 9.9,
            "risk_level": "Moderate",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        },
        "adjusted_plan": {
            "plan_name": "Balanced",
            "projected_corpus": 4189071.85,
            "gap_vs_target": -810928.15,
            "required_monthly_investment": 60499.80,
            "blended_expected_return": 9.9,
            "risk_level": "Moderate",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        },
        "impact": {
            "corpus_change": 772327.56,
            "gap_change": 772327.56,
            "investment_change": 0.0,
            "gap_improvement": True,
        },
    }


def test_calculate_whatif_scenario_expense_reduction(
    customer_profile, goal, historical_data
):
    """Test What-If calculation for expense reduction."""
    result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Moderate",
        historical_data=historical_data,
        adjustment_parameter="monthly_expenses",
        adjusted_value=50000,
        plan_name="Balanced",
    )
    
    # Check structure
    assert "scenario_name" in result
    assert "scenario_type" in result
    assert "adjustments" in result
    assert "base_plan" in result
    assert "adjusted_plan" in result
    assert "impact" in result
    
    # Check adjustments
    assert result["adjustments"]["parameter"] == "monthly_expenses"
    assert result["adjustments"]["original_value"] == 60000.0
    assert result["adjustments"]["adjusted_value"] == 50000.0
    assert result["adjustments"]["change"] == -10000.0
    
    # Check impact shows improvement
    assert result["impact"]["corpus_change"] > 0
    assert result["impact"]["gap_improvement"] is True


def test_calculate_whatif_scenario_income_increase(
    customer_profile, goal, historical_data
):
    """Test What-If calculation for income increase."""
    result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Moderate",
        historical_data=historical_data,
        adjustment_parameter="monthly_income",
        adjusted_value=120000,
        plan_name="Balanced",
    )
    
    # Check adjustments
    assert result["adjustments"]["parameter"] == "monthly_income"
    assert result["adjustments"]["original_value"] == 100000.0
    assert result["adjustments"]["adjusted_value"] == 120000.0
    assert result["adjustments"]["change"] == 20000.0
    
    # Check corpus increased
    assert result["adjusted_plan"]["projected_corpus"] > result["base_plan"]["projected_corpus"]


def test_calculate_whatif_scenario_sets_monthly_investment(
    customer_profile, goal, historical_data
):
    profile = {**customer_profile, "monthly_investment": 40_000}
    result = calculate_whatif_scenario(
        customer_profile=profile,
        goal=goal,
        risk_category="Moderate",
        historical_data=historical_data,
        adjustment_parameter="monthly_investment",
        adjusted_value=10_000,
        plan_name="Balanced",
    )

    assert result["adjustments"] == {
        "parameter": "monthly_investment",
        "original_value": 40_000.0,
        "adjusted_value": 10_000.0,
        "change": -30_000.0,
    }
    assert result["adjusted_plan"]["projected_corpus"] < result["base_plan"]["projected_corpus"]


def test_calculate_whatif_scenario_time_extension(
    customer_profile, goal, historical_data
):
    """Test What-If calculation for time horizon extension."""
    result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Moderate",
        historical_data=historical_data,
        adjustment_parameter="time_horizon_years",
        adjusted_value=7,
        plan_name="Balanced",
    )
    
    # Check adjustments
    assert result["adjustments"]["parameter"] == "time_horizon_years"
    assert result["adjustments"]["original_value"] == 5.0
    assert result["adjustments"]["adjusted_value"] == 7.0
    assert result["adjustments"]["change"] == 2.0
    
    # Extended time should increase corpus significantly
    assert result["adjusted_plan"]["projected_corpus"] > result["base_plan"]["projected_corpus"]


def test_calculate_whatif_scenario_conservative_plan(
    customer_profile, goal, historical_data
):
    """Test What-If calculation for Conservative plan."""
    result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Conservative",
        historical_data=historical_data,
        adjustment_parameter="monthly_expenses",
        adjusted_value=50000,
        plan_name="Conservative",
    )
    
    assert result["base_plan"]["plan_name"] == "Conservative"
    assert result["adjusted_plan"]["plan_name"] == "Conservative"
    assert result["base_plan"]["risk_level"] == "Conservative"


def test_calculate_whatif_scenario_growth_plan(
    customer_profile, goal, historical_data
):
    """Test What-If calculation for Growth plan."""
    result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Aggressive",
        historical_data=historical_data,
        adjustment_parameter="monthly_income",
        adjusted_value=120000,
        plan_name="Growth",
    )
    
    assert result["base_plan"]["plan_name"] == "Growth"
    assert result["adjusted_plan"]["plan_name"] == "Growth"
    assert result["base_plan"]["risk_level"] == "Aggressive"


def test_calculate_whatif_scenario_invalid_parameter(
    customer_profile, goal, historical_data
):
    """Test that invalid adjustment parameter raises error."""
    with pytest.raises(ValueError, match="adjustment_parameter must be one of"):
        calculate_whatif_scenario(
            customer_profile=customer_profile,
            goal=goal,
            risk_category="Moderate",
            historical_data=historical_data,
            adjustment_parameter="invalid_param",
            adjusted_value=50000,
        )


def test_calculate_whatif_scenario_invalid_plan_name(
    customer_profile, goal, historical_data
):
    """Test that invalid plan name raises error."""
    with pytest.raises(ValueError, match="plan_name must be one of"):
        calculate_whatif_scenario(
            customer_profile=customer_profile,
            goal=goal,
            risk_category="Moderate",
            historical_data=historical_data,
            adjustment_parameter="monthly_expenses",
            adjusted_value=50000,
            plan_name="InvalidPlan",
        )


def test_create_whatif_narration_prompt_contains_all_details(sample_whatif_result):
    """Test that prompt includes all What-If details."""
    prompt = create_whatif_narration_prompt(sample_whatif_result)
    
    # Check scenario name
    assert "Reduce Monthly Expenses" in prompt
    
    # Check adjustments
    assert "monthly_expenses" in prompt
    assert "60,000" in prompt or "60000" in prompt
    assert "50,000" in prompt or "50000" in prompt
    
    # Check base plan values
    assert "3,416,744.29" in prompt or "3416744.29" in prompt
    assert "SHORTFALL" in prompt
    
    # Check adjusted plan values
    assert "4,189,071.85" in prompt or "4189071.85" in prompt
    
    # Check impact
    assert "772,327.56" in prompt or "772327.56" in prompt


def test_create_whatif_narration_prompt_shows_improvement(sample_whatif_result):
    """Test that prompt correctly identifies improvement."""
    prompt = create_whatif_narration_prompt(sample_whatif_result)
    
    assert "IMPROVED" in prompt


def test_create_system_message_returns_string():
    """Test that system message is a non-empty string."""
    system_message = create_system_message()
    
    assert isinstance(system_message, str)
    assert len(system_message) > 0
    assert "what-if" in system_message.lower() or "what if" in system_message.lower()


@patch("app.genai.whatif_analyzer.generate_llm_response")
def test_narrate_whatif_scenario_calls_llm(mock_llm, sample_whatif_result):
    """Test that narrate_whatif_scenario calls LLM with proper parameters."""
    mock_llm.return_value = "This is a mocked What-If narration."
    
    result = narrate_whatif_scenario(sample_whatif_result)
    
    # Verify LLM was called
    assert mock_llm.called
    assert mock_llm.call_count == 1
    
    # Verify parameters
    call_args = mock_llm.call_args
    assert "prompt" in call_args.kwargs
    assert "system_message" in call_args.kwargs
    assert "temperature" in call_args.kwargs
    assert "max_tokens" in call_args.kwargs
    
    # Verify result
    assert result == "This is a mocked What-If narration."


@patch("app.genai.whatif_analyzer.generate_llm_response")
def test_narrate_whatif_scenario_returns_string(mock_llm, sample_whatif_result):
    """Test that narrate_whatif_scenario returns a string."""
    mock_llm.return_value = "Mocked narration text"
    
    result = narrate_whatif_scenario(sample_whatif_result)
    
    assert isinstance(result, str)
    assert len(result) > 0


@patch("app.genai.whatif_analyzer.generate_llm_response")
def test_narrate_whatif_scenario_custom_temperature(mock_llm, sample_whatif_result):
    """Test that custom temperature is passed to LLM."""
    mock_llm.return_value = "Mocked narration"
    
    narrate_whatif_scenario(sample_whatif_result, temperature=0.5)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["temperature"] == 0.5


@patch("app.genai.whatif_analyzer.generate_llm_response")
def test_narrate_whatif_scenario_custom_max_tokens(mock_llm, sample_whatif_result):
    """Test that custom max_tokens is passed to LLM."""
    mock_llm.return_value = "Mocked narration"
    
    narrate_whatif_scenario(sample_whatif_result, max_tokens=800)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["max_tokens"] == 800


def test_narrate_whatif_scenario_missing_fields():
    """Test that narrate_whatif_scenario raises error for missing fields."""
    incomplete_result = {
        "scenario_name": "Test",
        # Missing other required fields
    }
    
    with pytest.raises(ValueError, match="missing required fields"):
        narrate_whatif_scenario(incomplete_result)


@patch("app.genai.whatif_analyzer.generate_llm_response")
def test_analyze_and_narrate_whatif_combines_both(
    mock_llm, customer_profile, goal, historical_data
):
    """Test that analyze_and_narrate_whatif combines calculation and narration."""
    mock_llm.return_value = "Combined What-If narration"
    
    result = analyze_and_narrate_whatif(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Moderate",
        historical_data=historical_data,
        adjustment_parameter="monthly_expenses",
        adjusted_value=50000,
    )
    
    # Check it has all What-If calculation fields
    assert "scenario_name" in result
    assert "adjustments" in result
    assert "base_plan" in result
    assert "adjusted_plan" in result
    assert "impact" in result
    
    # Check it has the narration
    assert "narration" in result
    assert result["narration"] == "Combined What-If narration"
    
    # Verify LLM was called
    assert mock_llm.called


def test_calculate_whatif_scenario_all_numeric_fields_are_floats(
    customer_profile, goal, historical_data
):
    """Test that all numeric fields in result are floats, not numpy types."""
    result = calculate_whatif_scenario(
        customer_profile=customer_profile,
        goal=goal,
        risk_category="Moderate",
        historical_data=historical_data,
        adjustment_parameter="monthly_expenses",
        adjusted_value=50000,
    )
    
    # Check adjustments are floats
    assert isinstance(result["adjustments"]["original_value"], float)
    assert isinstance(result["adjustments"]["adjusted_value"], float)
    assert isinstance(result["adjustments"]["change"], float)
    
    # Check base_plan numeric fields are floats
    assert isinstance(result["base_plan"]["projected_corpus"], float)
    assert isinstance(result["base_plan"]["gap_vs_target"], float)
    assert isinstance(result["base_plan"]["required_monthly_investment"], float)
    
    # Check impact fields are correct types
    assert isinstance(result["impact"]["corpus_change"], float)
    assert isinstance(result["impact"]["gap_improvement"], bool)


def test_prompt_instructs_llm_not_to_calculate():
    """Test that prompt instructs LLM to only explain, not calculate."""
    whatif_result = {
        "scenario_name": "Test Scenario",
        "scenario_type": "test",
        "adjustments": {
            "parameter": "monthly_expenses",
            "original_value": 60000.0,
            "adjusted_value": 50000.0,
            "change": -10000.0,
        },
        "base_plan": {
            "plan_name": "Balanced",
            "projected_corpus": 3416744.29,
            "gap_vs_target": -1583255.71,
            "required_monthly_investment": 60499.80,
            "blended_expected_return": 9.9,
            "risk_level": "Moderate",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        },
        "adjusted_plan": {
            "plan_name": "Balanced",
            "projected_corpus": 4189071.85,
            "gap_vs_target": -810928.15,
            "required_monthly_investment": 60499.80,
            "blended_expected_return": 9.9,
            "risk_level": "Moderate",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        },
        "impact": {
            "corpus_change": 772327.56,
            "gap_change": 772327.56,
            "investment_change": 0.0,
            "gap_improvement": True,
        },
    }
    
    prompt = create_whatif_narration_prompt(whatif_result)
    
    # Verify instructions to not calculate
    assert "DO NOT calculate" in prompt or "do not calculate" in prompt.lower()
    assert "ONLY the numbers provided" in prompt or "only the numbers" in prompt.lower()
