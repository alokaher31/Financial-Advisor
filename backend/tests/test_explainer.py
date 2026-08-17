"""
Tests for the financial plan explainer module.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.genai.explainer import explain_plan, explain_multiple_plans
from app.genai.prompts.plan_explanation_prompt import (
    create_plan_explanation_prompt,
    create_system_message,
)


@pytest.fixture
def sample_conservative_plan():
    """Sample Conservative plan from generate_plans()."""
    return {
        "plan_name": "Conservative",
        "allocation": {
            "Equity": 20,
            "Debt": 50,
            "Gold": 15,
            "Real_Estate": 10,
            "Cash": 5,
        },
        "blended_expected_return": 8.33,
        "projected_corpus": 3123456.78,
        "gap_vs_target": -1876543.22,  # Shortfall
        "required_monthly_investment": 45123.45,
        "risk_level": "Conservative",
    }


@pytest.fixture
def sample_balanced_plan():
    """Sample Balanced plan from generate_plans()."""
    return {
        "plan_name": "Balanced",
        "allocation": {
            "Equity": 50,
            "Debt": 25,
            "Gold": 15,
            "Real_Estate": 10,
            "Cash": 0,
        },
        "blended_expected_return": 9.9,
        "projected_corpus": 3456789.01,
        "gap_vs_target": -1543210.99,  # Shortfall
        "required_monthly_investment": 42000.50,
        "risk_level": "Moderate",
    }


@pytest.fixture
def sample_growth_plan():
    """Sample Growth plan from generate_plans()."""
    return {
        "plan_name": "Growth",
        "allocation": {
            "Equity": 70,
            "Debt": 10,
            "Gold": 10,
            "Real_Estate": 10,
            "Cash": 0,
        },
        "blended_expected_return": 10.8,
        "projected_corpus": 3789012.34,
        "gap_vs_target": -1210987.66,  # Shortfall
        "required_monthly_investment": 38900.75,
        "risk_level": "Aggressive",
    }


@pytest.fixture
def plan_with_surplus():
    """Sample plan with surplus (exceeds target)."""
    return {
        "plan_name": "Growth",
        "allocation": {
            "Equity": 70,
            "Debt": 10,
            "Gold": 10,
            "Real_Estate": 10,
            "Cash": 0,
        },
        "blended_expected_return": 12.5,
        "projected_corpus": 5500000.00,
        "gap_vs_target": 500000.00,  # Surplus
        "required_monthly_investment": 35000.00,
        "risk_level": "Aggressive",
    }


@pytest.fixture
def plan_exact_match():
    """Sample plan that exactly meets target."""
    return {
        "plan_name": "Balanced",
        "allocation": {
            "Equity": 50,
            "Debt": 25,
            "Gold": 15,
            "Real_Estate": 10,
            "Cash": 0,
        },
        "blended_expected_return": 10.0,
        "projected_corpus": 5000000.00,
        "gap_vs_target": 0.0,  # Exact match
        "required_monthly_investment": 40000.00,
        "risk_level": "Moderate",
    }


def test_create_plan_explanation_prompt_contains_all_plan_details(sample_conservative_plan):
    """Test that the prompt includes all plan details."""
    prompt = create_plan_explanation_prompt(sample_conservative_plan)
    
    assert "Conservative" in prompt
    assert "Conservative" in prompt  # risk_level
    assert "8.33" in prompt
    assert "3,123,456.78" in prompt or "3123456.78" in prompt
    assert "45,123.45" in prompt or "45123.45" in prompt
    assert "SHORTFALL" in prompt
    assert "Equity: 20%" in prompt
    assert "Debt: 50%" in prompt


def test_create_plan_explanation_prompt_shows_shortfall(sample_balanced_plan):
    """Test that prompt correctly identifies shortfall."""
    prompt = create_plan_explanation_prompt(sample_balanced_plan)
    
    assert "SHORTFALL" in prompt
    assert "1,543,210.99" in prompt or "1543210.99" in prompt


def test_create_plan_explanation_prompt_shows_surplus(plan_with_surplus):
    """Test that prompt correctly identifies surplus."""
    prompt = create_plan_explanation_prompt(plan_with_surplus)
    
    assert "SURPLUS" in prompt
    assert "500,000.00" in prompt or "500000.00" in prompt


def test_create_plan_explanation_prompt_shows_exact_match(plan_exact_match):
    """Test that prompt correctly identifies exact match."""
    prompt = create_plan_explanation_prompt(plan_exact_match)
    
    assert "EXACT MATCH" in prompt


def test_create_system_message_returns_string():
    """Test that system message is a non-empty string."""
    system_message = create_system_message()
    
    assert isinstance(system_message, str)
    assert len(system_message) > 0
    assert "financial advisor" in system_message.lower()


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_calls_llm_with_correct_parameters(
    mock_llm, sample_conservative_plan
):
    """Test that explain_plan calls the LLM with proper parameters."""
    mock_llm.return_value = "This is a mocked explanation of the Conservative plan."
    
    result = explain_plan(sample_conservative_plan)
    
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
    assert result == "This is a mocked explanation of the Conservative plan."


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_returns_string(mock_llm, sample_balanced_plan):
    """Test that explain_plan returns a string."""
    mock_llm.return_value = "Mocked Balanced plan explanation."
    
    result = explain_plan(sample_balanced_plan)
    
    assert isinstance(result, str)
    assert len(result) > 0


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_with_custom_temperature(mock_llm, sample_growth_plan):
    """Test that custom temperature is passed to LLM."""
    mock_llm.return_value = "Mocked explanation"
    
    explain_plan(sample_growth_plan, temperature=0.5)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["temperature"] == 0.5


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_with_custom_max_tokens(mock_llm, sample_conservative_plan):
    """Test that custom max_tokens is passed to LLM."""
    mock_llm.return_value = "Mocked explanation"
    
    explain_plan(sample_conservative_plan, max_tokens=800)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["max_tokens"] == 800


def test_explain_plan_raises_error_for_missing_fields():
    """Test that explain_plan raises ValueError for missing required fields."""
    incomplete_plan = {
        "plan_name": "Conservative",
        "allocation": {"Equity": 20},
        # Missing other required fields
    }
    
    with pytest.raises(ValueError, match="missing required fields"):
        explain_plan(incomplete_plan)


def test_explain_plan_raises_error_for_invalid_allocation():
    """Test that explain_plan raises ValueError for non-dict allocation."""
    invalid_plan = {
        "plan_name": "Conservative",
        "allocation": "invalid",  # Should be dict
        "blended_expected_return": 8.33,
        "projected_corpus": 3123456.78,
        "gap_vs_target": -1876543.22,
        "required_monthly_investment": 45123.45,
        "risk_level": "Conservative",
    }
    
    with pytest.raises(ValueError, match="allocation must be a dictionary"):
        explain_plan(invalid_plan)


@patch("app.genai.explainer.generate_llm_response")
def test_explain_multiple_plans(
    mock_llm,
    sample_conservative_plan,
    sample_balanced_plan,
    sample_growth_plan,
):
    """Test explaining multiple plans at once."""
    mock_llm.side_effect = [
        "Conservative explanation",
        "Balanced explanation",
        "Growth explanation",
    ]
    
    plans = [sample_conservative_plan, sample_balanced_plan, sample_growth_plan]
    explanations = explain_multiple_plans(plans)
    
    assert len(explanations) == 3
    assert explanations[0] == "Conservative explanation"
    assert explanations[1] == "Balanced explanation"
    assert explanations[2] == "Growth explanation"
    assert mock_llm.call_count == 3


@patch("app.genai.explainer.generate_llm_response")
def test_explain_multiple_plans_with_custom_parameters(
    mock_llm, sample_conservative_plan
):
    """Test that custom parameters are passed when explaining multiple plans."""
    mock_llm.return_value = "Mocked explanation"
    
    plans = [sample_conservative_plan]
    explain_multiple_plans(plans, temperature=0.3, max_tokens=500)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["temperature"] == 0.3
    assert call_args.kwargs["max_tokens"] == 500


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_prompt_includes_plan_name(mock_llm, sample_conservative_plan):
    """Test that the generated prompt includes the plan name."""
    mock_llm.return_value = "Mocked explanation"
    
    explain_plan(sample_conservative_plan)
    
    call_args = mock_llm.call_args
    prompt = call_args.kwargs["prompt"]
    assert "Conservative" in prompt


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_prompt_includes_all_numeric_values(
    mock_llm, sample_balanced_plan
):
    """Test that the prompt includes all numeric values from the plan."""
    mock_llm.return_value = "Mocked explanation"
    
    explain_plan(sample_balanced_plan)
    
    call_args = mock_llm.call_args
    prompt = call_args.kwargs["prompt"]
    
    # Check all numeric values are in the prompt
    assert "9.9" in prompt  # blended_expected_return
    assert "3,456,789.01" in prompt or "3456789.01" in prompt  # projected_corpus
    assert "42,000.50" in prompt or "42000.50" in prompt  # required_monthly_investment


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_uses_system_message(mock_llm, sample_growth_plan):
    """Test that explain_plan uses the system message."""
    mock_llm.return_value = "Mocked explanation"
    
    explain_plan(sample_growth_plan)
    
    call_args = mock_llm.call_args
    system_message = call_args.kwargs["system_message"]
    assert isinstance(system_message, str)
    assert len(system_message) > 0


@patch("app.genai.explainer.generate_llm_response")
def test_explain_plan_handles_zero_required_investment(mock_llm):
    """Test explaining a plan where no additional investment is needed."""
    plan_no_investment_needed = {
        "plan_name": "Growth",
        "allocation": {"Equity": 70, "Debt": 10, "Gold": 10, "Real_Estate": 10, "Cash": 0},
        "blended_expected_return": 12.0,
        "projected_corpus": 6000000.00,
        "gap_vs_target": 1000000.00,  # Surplus
        "required_monthly_investment": 0.0,  # No investment needed
        "risk_level": "Aggressive",
    }
    
    mock_llm.return_value = "You already have enough to meet your goal."
    
    result = explain_plan(plan_no_investment_needed)
    
    assert mock_llm.called
    assert isinstance(result, str)


def test_prompt_instructs_llm_not_to_calculate():
    """Test that prompt instructs LLM to only explain, not calculate."""
    plan = {
        "plan_name": "Balanced",
        "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
        "blended_expected_return": 9.9,
        "projected_corpus": 3456789.01,
        "gap_vs_target": -1543210.99,
        "required_monthly_investment": 42000.50,
        "risk_level": "Moderate",
    }
    
    prompt = create_plan_explanation_prompt(plan)
    
    # Verify instructions to not calculate
    assert "DO NOT calculate" in prompt or "do not calculate" in prompt.lower()
    assert "ONLY the numbers provided" in prompt or "only the numbers provided" in prompt.lower()
