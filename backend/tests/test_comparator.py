"""
Tests for the financial plan comparator module.
"""

import pytest
from unittest.mock import patch, MagicMock

from app.genai.comparator import compare_plans, compare_plans_structured
from app.genai.prompts.plan_comparison_prompt import (
    create_plan_comparison_prompt,
    create_system_message,
)


@pytest.fixture
def sample_three_plans():
    """Sample three plans from generate_plans()."""
    return [
        {
            "plan_name": "Conservative",
            "allocation": {
                "Equity": 20,
                "Debt": 50,
                "Gold": 15,
                "Real_Estate": 10,
                "Cash": 5,
            },
            "blended_expected_return": 8.33,
            "projected_corpus": 3266924.06,
            "gap_vs_target": -1733075.94,  # Shortfall
            "required_monthly_investment": 63387.50,
            "risk_level": "Conservative",
        },
        {
            "plan_name": "Balanced",
            "allocation": {
                "Equity": 50,
                "Debt": 25,
                "Gold": 15,
                "Real_Estate": 10,
                "Cash": 0,
            },
            "blended_expected_return": 9.9,
            "projected_corpus": 3416744.29,
            "gap_vs_target": -1583255.71,  # Shortfall
            "required_monthly_investment": 60499.80,
            "risk_level": "Moderate",
        },
        {
            "plan_name": "Growth",
            "allocation": {
                "Equity": 70,
                "Debt": 10,
                "Gold": 10,
                "Real_Estate": 10,
                "Cash": 0,
            },
            "blended_expected_return": 10.8,
            "projected_corpus": 3506225.89,
            "gap_vs_target": -1493774.11,  # Shortfall
            "required_monthly_investment": 58885.51,
            "risk_level": "Aggressive",
        },
    ]


@pytest.fixture
def plans_with_surplus():
    """Sample plans where some have surplus."""
    return [
        {
            "plan_name": "Conservative",
            "allocation": {"Equity": 20, "Debt": 50, "Gold": 15, "Real_Estate": 10, "Cash": 5},
            "blended_expected_return": 8.33,
            "projected_corpus": 5200000.00,
            "gap_vs_target": 200000.00,  # Surplus
            "required_monthly_investment": 45000.00,
            "risk_level": "Conservative",
        },
        {
            "plan_name": "Balanced",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
            "blended_expected_return": 9.9,
            "projected_corpus": 5500000.00,
            "gap_vs_target": 500000.00,  # Surplus
            "required_monthly_investment": 42000.00,
            "risk_level": "Moderate",
        },
        {
            "plan_name": "Growth",
            "allocation": {"Equity": 70, "Debt": 10, "Gold": 10, "Real_Estate": 10, "Cash": 0},
            "blended_expected_return": 10.8,
            "projected_corpus": 5800000.00,
            "gap_vs_target": 800000.00,  # Surplus
            "required_monthly_investment": 38000.00,
            "risk_level": "Aggressive",
        },
    ]


def test_create_plan_comparison_prompt_contains_all_plan_details(sample_three_plans):
    """Test that the comparison prompt includes details from all three plans."""
    prompt = create_plan_comparison_prompt(sample_three_plans)
    
    # Check all plan names
    assert "Conservative" in prompt
    assert "Balanced" in prompt
    assert "Growth" in prompt
    
    # Check risk levels
    assert "Conservative" in prompt
    assert "Moderate" in prompt
    assert "Aggressive" in prompt
    
    # Check expected returns
    assert "8.33" in prompt
    assert "9.9" in prompt
    assert "10.8" in prompt
    
    # Check all three plans have their data
    assert "3,266,924.06" in prompt or "3266924.06" in prompt
    assert "3,416,744.29" in prompt or "3416744.29" in prompt
    assert "3,506,225.89" in prompt or "3506225.89" in prompt


def test_create_plan_comparison_prompt_shows_shortfalls(sample_three_plans):
    """Test that prompt correctly identifies shortfalls for all plans."""
    prompt = create_plan_comparison_prompt(sample_three_plans)
    
    # All three plans have shortfalls (appears in plan data and instructions)
    assert prompt.count("SHORTFALL") >= 3


def test_create_plan_comparison_prompt_shows_surplus(plans_with_surplus):
    """Test that prompt correctly identifies surplus."""
    prompt = create_plan_comparison_prompt(plans_with_surplus)
    
    # All three plans have surplus (appears in plan data and instructions)
    assert prompt.count("SURPLUS") >= 3


def test_create_plan_comparison_prompt_shows_allocation_differences(sample_three_plans):
    """Test that prompt includes allocation percentages for each plan."""
    prompt = create_plan_comparison_prompt(sample_three_plans)
    
    # Conservative allocations
    assert "Equity: 20%" in prompt
    assert "Debt: 50%" in prompt
    
    # Balanced allocations
    assert "Equity: 50%" in prompt
    assert "Debt: 25%" in prompt
    
    # Growth allocations
    assert "Equity: 70%" in prompt
    assert "Debt: 10%" in prompt


def test_create_plan_comparison_prompt_raises_error_for_wrong_count():
    """Test that prompt creation fails if not exactly 3 plans."""
    with pytest.raises(ValueError, match="Expected exactly 3 plans"):
        create_plan_comparison_prompt([{"plan_name": "Test"}])
    
    with pytest.raises(ValueError, match="Expected exactly 3 plans"):
        create_plan_comparison_prompt([])


def test_create_system_message_returns_string():
    """Test that system message is a non-empty string."""
    system_message = create_system_message()
    
    assert isinstance(system_message, str)
    assert len(system_message) > 0
    assert "financial advisor" in system_message.lower()


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_calls_llm_with_correct_parameters(mock_llm, sample_three_plans):
    """Test that compare_plans calls the LLM with proper parameters."""
    mock_llm.return_value = "This is a mocked comparison of the three plans."
    
    result = compare_plans(sample_three_plans)
    
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
    assert result == "This is a mocked comparison of the three plans."


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_returns_string(mock_llm, sample_three_plans):
    """Test that compare_plans returns a string."""
    mock_llm.return_value = "Mocked comparison text"
    
    result = compare_plans(sample_three_plans)
    
    assert isinstance(result, str)
    assert len(result) > 0


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_with_custom_temperature(mock_llm, sample_three_plans):
    """Test that custom temperature is passed to LLM."""
    mock_llm.return_value = "Mocked comparison"
    
    compare_plans(sample_three_plans, temperature=0.5)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["temperature"] == 0.5


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_with_custom_max_tokens(mock_llm, sample_three_plans):
    """Test that custom max_tokens is passed to LLM."""
    mock_llm.return_value = "Mocked comparison"
    
    compare_plans(sample_three_plans, max_tokens=1000)
    
    call_args = mock_llm.call_args
    assert call_args.kwargs["max_tokens"] == 1000


def test_compare_plans_raises_error_for_wrong_plan_count():
    """Test that compare_plans raises ValueError for wrong number of plans."""
    # Too few plans
    with pytest.raises(ValueError, match="Expected exactly 3 plans"):
        compare_plans([{"plan_name": "Test"}])
    
    # Too many plans
    four_plans = [{"plan_name": f"Plan{i}"} for i in range(4)]
    with pytest.raises(ValueError, match="Expected exactly 3 plans"):
        compare_plans(four_plans)


def test_compare_plans_raises_error_for_non_list():
    """Test that compare_plans raises ValueError for non-list input."""
    with pytest.raises(ValueError, match="plans must be a list"):
        compare_plans("not a list")


def test_compare_plans_raises_error_for_missing_fields():
    """Test that compare_plans raises ValueError for missing required fields."""
    incomplete_plans = [
        {"plan_name": "Conservative", "allocation": {"Equity": 20}},
        {"plan_name": "Balanced", "allocation": {"Equity": 50}},
        {"plan_name": "Growth", "allocation": {"Equity": 70}},
    ]
    
    with pytest.raises(ValueError, match="missing required fields"):
        compare_plans(incomplete_plans)


def test_compare_plans_raises_error_for_invalid_allocation():
    """Test that compare_plans raises ValueError for non-dict allocation."""
    invalid_plans = [
        {
            "plan_name": "Conservative",
            "allocation": "invalid",  # Should be dict
            "blended_expected_return": 8.33,
            "projected_corpus": 3266924.06,
            "gap_vs_target": -1733075.94,
            "required_monthly_investment": 63387.50,
            "risk_level": "Conservative",
        },
        {
            "plan_name": "Balanced",
            "allocation": {"Equity": 50},
            "blended_expected_return": 9.9,
            "projected_corpus": 3416744.29,
            "gap_vs_target": -1583255.71,
            "required_monthly_investment": 60499.80,
            "risk_level": "Moderate",
        },
        {
            "plan_name": "Growth",
            "allocation": {"Equity": 70},
            "blended_expected_return": 10.8,
            "projected_corpus": 3506225.89,
            "gap_vs_target": -1493774.11,
            "required_monthly_investment": 58885.51,
            "risk_level": "Aggressive",
        },
    ]
    
    with pytest.raises(ValueError, match="allocation must be a dictionary"):
        compare_plans(invalid_plans)


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_prompt_includes_all_plan_names(mock_llm, sample_three_plans):
    """Test that the generated prompt includes all plan names."""
    mock_llm.return_value = "Mocked comparison"
    
    compare_plans(sample_three_plans)
    
    call_args = mock_llm.call_args
    prompt = call_args.kwargs["prompt"]
    
    assert "Conservative" in prompt
    assert "Balanced" in prompt
    assert "Growth" in prompt


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_prompt_includes_trade_offs_instruction(mock_llm, sample_three_plans):
    """Test that the prompt includes instructions about trade-offs."""
    mock_llm.return_value = "Mocked comparison"
    
    compare_plans(sample_three_plans)
    
    call_args = mock_llm.call_args
    prompt = call_args.kwargs["prompt"]
    
    assert "trade-off" in prompt.lower() or "tradeoff" in prompt.lower()


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_uses_system_message(mock_llm, sample_three_plans):
    """Test that compare_plans uses the system message."""
    mock_llm.return_value = "Mocked comparison"
    
    compare_plans(sample_three_plans)
    
    call_args = mock_llm.call_args
    system_message = call_args.kwargs["system_message"]
    assert isinstance(system_message, str)
    assert len(system_message) > 0


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_structured_returns_dict(mock_llm, sample_three_plans):
    """Test that compare_plans_structured returns a structured dictionary."""
    mock_llm.return_value = "Mocked comparison text"
    
    result = compare_plans_structured(sample_three_plans)
    
    assert isinstance(result, dict)
    assert "plans" in result
    assert "comparison" in result
    assert "plan_names" in result
    assert "risk_levels" in result


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_structured_includes_original_plans(mock_llm, sample_three_plans):
    """Test that structured response includes original plan data."""
    mock_llm.return_value = "Mocked comparison"
    
    result = compare_plans_structured(sample_three_plans)
    
    assert result["plans"] == sample_three_plans
    assert len(result["plans"]) == 3


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_structured_extracts_plan_names(mock_llm, sample_three_plans):
    """Test that structured response extracts plan names correctly."""
    mock_llm.return_value = "Mocked comparison"
    
    result = compare_plans_structured(sample_three_plans)
    
    assert result["plan_names"] == ["Conservative", "Balanced", "Growth"]


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_structured_extracts_risk_levels(mock_llm, sample_three_plans):
    """Test that structured response extracts risk levels correctly."""
    mock_llm.return_value = "Mocked comparison"
    
    result = compare_plans_structured(sample_three_plans)
    
    assert result["risk_levels"] == ["Conservative", "Moderate", "Aggressive"]


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_structured_includes_comparison_text(mock_llm, sample_three_plans):
    """Test that structured response includes the comparison text."""
    mock_comparison = "This is a detailed comparison of the three plans..."
    mock_llm.return_value = mock_comparison
    
    result = compare_plans_structured(sample_three_plans)
    
    assert result["comparison"] == mock_comparison


def test_prompt_instructs_llm_not_to_calculate():
    """Test that prompt instructs LLM to only explain, not calculate."""
    plans = [
        {
            "plan_name": "Conservative",
            "allocation": {"Equity": 20, "Debt": 50, "Gold": 15, "Real_Estate": 10, "Cash": 5},
            "blended_expected_return": 8.33,
            "projected_corpus": 3266924.06,
            "gap_vs_target": -1733075.94,
            "required_monthly_investment": 63387.50,
            "risk_level": "Conservative",
        },
        {
            "plan_name": "Balanced",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
            "blended_expected_return": 9.9,
            "projected_corpus": 3416744.29,
            "gap_vs_target": -1583255.71,
            "required_monthly_investment": 60499.80,
            "risk_level": "Moderate",
        },
        {
            "plan_name": "Growth",
            "allocation": {"Equity": 70, "Debt": 10, "Gold": 10, "Real_Estate": 10, "Cash": 0},
            "blended_expected_return": 10.8,
            "projected_corpus": 3506225.89,
            "gap_vs_target": -1493774.11,
            "required_monthly_investment": 58885.51,
            "risk_level": "Aggressive",
        },
    ]
    
    prompt = create_plan_comparison_prompt(plans)
    
    # Verify instructions to not calculate
    assert "DO NOT calculate" in prompt or "do not calculate" in prompt.lower()
    assert "ONLY the numbers provided" in prompt or "only the numbers" in prompt.lower()


@patch("app.genai.comparator.generate_llm_response")
def test_compare_plans_with_zero_required_investment(mock_llm):
    """Test comparing plans where some have zero required investment."""
    plans_no_investment = [
        {
            "plan_name": "Conservative",
            "allocation": {"Equity": 20, "Debt": 50, "Gold": 15, "Real_Estate": 10, "Cash": 5},
            "blended_expected_return": 8.33,
            "projected_corpus": 6000000.00,
            "gap_vs_target": 1000000.00,
            "required_monthly_investment": 0.0,
            "risk_level": "Conservative",
        },
        {
            "plan_name": "Balanced",
            "allocation": {"Equity": 50, "Debt": 25, "Gold": 15, "Real_Estate": 10, "Cash": 0},
            "blended_expected_return": 9.9,
            "projected_corpus": 6500000.00,
            "gap_vs_target": 1500000.00,
            "required_monthly_investment": 0.0,
            "risk_level": "Moderate",
        },
        {
            "plan_name": "Growth",
            "allocation": {"Equity": 70, "Debt": 10, "Gold": 10, "Real_Estate": 10, "Cash": 0},
            "blended_expected_return": 10.8,
            "projected_corpus": 7000000.00,
            "gap_vs_target": 2000000.00,
            "required_monthly_investment": 0.0,
            "risk_level": "Aggressive",
        },
    ]
    
    mock_llm.return_value = "All three plans already meet your goal."
    
    result = compare_plans(plans_no_investment)
    
    assert mock_llm.called
    assert isinstance(result, str)
