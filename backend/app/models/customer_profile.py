"""
Customer Profile Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class CustomerProfileBase(BaseModel):
    """Base model for customer profile data."""
    name: str = Field(..., min_length=1, max_length=200, description="Customer name")
    age: int = Field(..., ge=18, le=100, description="Customer age")
    occupation: str = Field(..., min_length=1, max_length=200, description="Customer occupation")
    monthly_income: float = Field(..., ge=0, description="Monthly income in currency")
    monthly_expenses: float = Field(..., ge=0, description="Monthly expenses in currency")
    total_assets: float = Field(..., ge=0, description="Total assets value")
    total_liabilities: float = Field(..., ge=0, description="Total liabilities value")
    
    @field_validator('monthly_expenses')
    @classmethod
    def validate_expenses(cls, v, info):
        """Ensure monthly expenses don't exceed monthly income by too much."""
        if 'monthly_income' in info.data and v > info.data['monthly_income'] * 2:
            raise ValueError("Monthly expenses seem unusually high compared to income")
        return v

    @model_validator(mode="after")
    def validate_income_for_liabilities(self):
        if self.monthly_income == 0 and self.total_liabilities > 0:
            raise ValueError(
                "Monthly income must be greater than zero when liabilities are present"
            )
        return self


class CustomerProfileCreate(CustomerProfileBase):
    """Model for creating a new customer profile."""
    pass


class CustomerProfileUpdate(BaseModel):
    """Model for updating an existing customer profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    age: Optional[int] = Field(None, ge=18, le=100)
    occupation: Optional[str] = Field(None, min_length=1, max_length=200)
    monthly_income: Optional[float] = Field(None, ge=0)
    monthly_expenses: Optional[float] = Field(None, ge=0)
    total_assets: Optional[float] = Field(None, ge=0)
    total_liabilities: Optional[float] = Field(None, ge=0)


class CustomerProfile(CustomerProfileBase):
    """Model for customer profile response with database fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    net_worth: float = Field(..., description="Calculated net worth")
    monthly_surplus: float = Field(..., description="Calculated monthly surplus")
    debt_to_income_ratio: float = Field(
        ...,
        description="Total liabilities divided by annual gross income",
    )
    created_at: datetime
    updated_at: datetime
    
class FinancialSummary(BaseModel):
    """Financial summary calculations for a customer."""
    net_worth: float = Field(..., description="Total assets minus total liabilities")
    monthly_surplus: float = Field(..., description="Monthly income minus monthly expenses")
    debt_to_income_ratio: float = Field(
        ...,
        description="Total liabilities divided by annual gross income",
    )
    annual_savings_capacity: float = Field(..., description="Monthly surplus times 12")
    financial_health_score: str = Field(..., description="Overall financial health rating")
