"""
Financial Goal Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class GoalType(str, Enum):
    """Types of financial goals."""
    RETIREMENT = "retirement"
    EDUCATION = "education"
    HOME_PURCHASE = "home_purchase"
    VEHICLE = "vehicle"
    VACATION = "vacation"
    EMERGENCY_FUND = "emergency_fund"
    INVESTMENT = "investment"
    DEBT_PAYOFF = "debt_payoff"
    OTHER = "other"


class GoalPriority(str, Enum):
    """Priority levels for goals."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GoalBase(BaseModel):
    """Base model for financial goal data."""
    goal_type: GoalType = Field(..., description="Type of financial goal")
    goal_name: str = Field(..., min_length=1, max_length=200, description="Name of the goal")
    target_amount: float = Field(..., gt=0, description="Target amount to achieve")
    current_savings: float = Field(0, ge=0, description="Current amount saved towards goal")
    time_horizon_years: int = Field(..., gt=0, le=50, description="Years until goal should be achieved")
    priority: GoalPriority = Field(GoalPriority.MEDIUM, description="Priority level of the goal")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes about the goal")
    
    @field_validator('current_savings')
    @classmethod
    def validate_current_savings(cls, v, info):
        """Ensure current savings don't exceed target amount."""
        if 'target_amount' in info.data and v > info.data['target_amount']:
            raise ValueError("Current savings cannot exceed target amount")
        return v


class GoalCreate(GoalBase):
    """Model for creating a new financial goal."""
    customer_id: int = Field(..., gt=0, description="ID of the customer this goal belongs to")


class GoalUpdate(BaseModel):
    """Model for updating an existing financial goal."""
    goal_type: Optional[GoalType] = None
    goal_name: Optional[str] = Field(None, min_length=1, max_length=200)
    target_amount: Optional[float] = Field(None, gt=0)
    current_savings: Optional[float] = Field(None, ge=0)
    time_horizon_years: Optional[int] = Field(None, gt=0, le=50)
    priority: Optional[GoalPriority] = None
    notes: Optional[str] = Field(None, max_length=1000)


class Goal(GoalBase):
    """Model for goal response with database fields."""
    id: int
    customer_id: int
    required_monthly_saving: float = Field(..., description="Calculated monthly saving required")
    is_achievable: bool = Field(..., description="Whether goal is achievable with current finances")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class GoalCalculation(BaseModel):
    """Detailed calculation results for a financial goal."""
    goal_id: int
    goal_name: str
    target_amount: float
    current_savings: float
    amount_needed: float = Field(..., description="Target minus current savings")
    time_horizon_years: int
    required_monthly_saving: float = Field(..., description="Monthly amount needed to reach goal")
    required_annual_saving: float = Field(..., description="Annual amount needed to reach goal")
    total_savings_required: float = Field(..., description="Total amount to save over time horizon")
    assumed_return_rate: float = Field(..., description="Annual return rate used in calculation")
    is_achievable: bool = Field(..., description="Based on customer's monthly surplus")
    achievability_percentage: float = Field(..., description="What percentage of the goal can be achieved")
