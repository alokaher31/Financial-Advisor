"""
Financial Plan Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, model_validator


class PlanStatus(str, Enum):
    """Status of a financial plan."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class AssetAllocation(BaseModel):
    """Asset allocation breakdown."""
    equity_percentage: float = Field(..., ge=0, le=100, description="Percentage in equities")
    debt_percentage: float = Field(..., ge=0, le=100, description="Percentage in debt instruments")
    cash_percentage: float = Field(..., ge=0, le=100, description="Percentage in cash/liquid assets")
    gold_percentage: float = Field(0, ge=0, le=100, description="Percentage in gold")
    real_estate_percentage: float = Field(0, ge=0, le=100, description="Percentage in real estate")
    
    @property
    def total_percentage(self) -> float:
        """Calculate total allocation percentage."""
        return (
            self.equity_percentage
            + self.debt_percentage
            + self.cash_percentage
            + self.gold_percentage
            + self.real_estate_percentage
        )

    @model_validator(mode="after")
    def validate_total_percentage(self):
        if abs(self.total_percentage - 100) > 1e-6:
            raise ValueError("Asset allocation percentages must total 100")
        return self


class GoalAllocation(BaseModel):
    """Allocation of savings towards a specific goal."""
    goal_id: int = Field(..., description="ID of the goal")
    goal_name: str = Field(..., description="Name of the goal")
    monthly_allocation: float = Field(..., ge=0, description="Monthly amount allocated")
    priority_rank: int = Field(..., ge=1, description="Priority ranking of this goal")


class MonthlyBreakdown(BaseModel):
    """Detailed monthly financial breakdown."""
    total_income: float = Field(..., ge=0)
    total_expenses: float = Field(..., ge=0)
    available_for_savings: float = Field(..., ge=0)
    allocated_to_goals: float = Field(..., ge=0)
    emergency_fund_contribution: float = Field(..., ge=0)
    discretionary_savings: float = Field(..., ge=0)
    surplus_deficit: float = Field(...)


class PlanCreateRequest(BaseModel):
    """Request model for generating a financial plan."""
    customer_id: int = Field(..., gt=0, description="ID of the customer")
    goal_ids: List[int] = Field(
        ...,
        min_length=1,
        max_length=1,
        description="Exactly one goal ID; multi-goal allocation is not yet supported",
    )
    risk_assessment_id: Optional[int] = Field(None, description="ID of risk assessment to use")
    custom_parameters: Optional[Dict[str, Any]] = Field(
        None, 
        description="Custom parameters for plan generation"
    )


class PlanBase(BaseModel):
    """Base model for financial plan data."""
    customer_id: int
    plan_name: str = Field(..., min_length=1, max_length=200, description="Name of the financial plan")
    status: PlanStatus = Field(PlanStatus.DRAFT, description="Current status of the plan")
    asset_allocation: AssetAllocation = Field(..., description="Recommended asset allocation")
    monthly_savings_target: float = Field(..., ge=0, description="Total monthly savings target")
    goal_allocations: List[GoalAllocation] = Field(..., description="Allocation per goal")
    monthly_breakdown: MonthlyBreakdown = Field(..., description="Detailed monthly breakdown")
    assumptions: Dict[str, Any] = Field(..., description="Assumptions used in plan generation")
    notes: Optional[str] = Field(None, max_length=2000, description="Additional notes about the plan")


class PlanCreate(PlanBase):
    """Model for creating a new financial plan."""
    pass


class PlanUpdate(BaseModel):
    """Model for updating an existing financial plan."""
    plan_name: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[PlanStatus] = None
    notes: Optional[str] = Field(None, max_length=2000)


class Plan(PlanBase):
    """Model for plan response with database fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    
class PlanComparison(BaseModel):
    """Model for comparing two financial plans."""
    plan_a_id: int
    plan_b_id: int
    plan_a_name: str
    plan_b_name: str
    comparison_summary: str = Field(..., description="AI-generated comparison summary")
    key_differences: List[str] = Field(..., description="Key differences between plans")
    recommendation: str = Field(..., description="Recommendation on which plan to choose")


class WhatIfScenario(BaseModel):
    """Model for what-if scenario analysis."""
    scenario_name: str = Field(..., description="Name of the scenario")
    base_plan_id: int = Field(..., description="Base plan to compare against")
    parameter_changes: Dict[str, Any] = Field(..., description="Parameters to change")
    impact_analysis: str = Field(..., description="AI-generated impact analysis")
    projected_outcomes: Dict[str, Any] = Field(..., description="Projected outcomes")


class PlanExplanation(BaseModel):
    """Model for AI-generated plan explanation."""
    plan_id: int
    summary: str = Field(..., description="High-level summary of the plan")
    detailed_explanation: str = Field(..., description="Detailed explanation of the plan")
    key_recommendations: List[str] = Field(..., description="Key recommendations")
    risks_and_considerations: List[str] = Field(..., description="Risks and considerations")
    action_items: List[str] = Field(..., description="Suggested action items")
