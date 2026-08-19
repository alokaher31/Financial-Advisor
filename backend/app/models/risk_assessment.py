"""
Risk Assessment Pydantic models for request/response validation.
"""

from datetime import datetime
from typing import Dict, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RiskAnswers(BaseModel):
    """Model for risk assessment questionnaire answers."""
    answers: Dict[str, str] = Field(
        ..., 
        description="Dictionary mapping question IDs to selected answer options"
    )
    
    @field_validator('answers')
    @classmethod
    def validate_answers(cls, v):
        """Ensure all required question IDs are present."""
        required_questions = {
            "investment_experience", "market_drop_reaction", "income_stability",
            "investment_time_horizon", "primary_goal", "volatility_comfort",
            "investment_knowledge", "emergency_fund_coverage",
            "debt_payment_pressure", "loss_capacity",
        }
        provided_questions = set(v.keys())
        
        if not required_questions.issubset(provided_questions):
            missing = required_questions - provided_questions
            raise ValueError(f"Missing required questions: {missing}")
        
        return v


class RiskAssessmentCreate(BaseModel):
    """Model for creating a new risk assessment."""
    customer_id: int = Field(..., gt=0, description="ID of the customer")
    answers: Dict[str, str] = Field(..., description="Risk questionnaire answers")


class RiskAssessmentBase(BaseModel):
    """Base model for risk assessment data."""
    customer_id: int
    risk_score: int = Field(..., ge=0, le=100, description="Calculated risk score (0-100)")
    risk_category: str = Field(..., description="Risk category: Conservative, Moderate, or Aggressive")
    answers: Dict[str, str] = Field(..., description="Risk questionnaire answers")


class RiskAssessment(RiskAssessmentBase):
    """Model for risk assessment response with database fields."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    
class RiskProfile(BaseModel):
    """Comprehensive risk profile with recommendations."""
    risk_score: int = Field(..., ge=0, le=100)
    risk_category: str = Field(..., description="Conservative, Moderate, or Aggressive")
    equity_allocation: float = Field(..., ge=0, le=100, description="Recommended equity percentage")
    debt_allocation: float = Field(..., ge=0, le=100, description="Recommended debt percentage")
    cash_allocation: float = Field(..., ge=0, le=100, description="Recommended cash percentage")
    risk_tolerance_description: str = Field(..., description="Detailed description of risk profile")
    investment_recommendations: list[str] = Field(..., description="List of investment recommendations")
    
    @field_validator('equity_allocation', 'debt_allocation', 'cash_allocation')
    @classmethod
    def validate_allocation(cls, v):
        """Ensure allocation percentages are valid."""
        if not 0 <= v <= 100:
            raise ValueError("Allocation must be between 0 and 100")
        return v


class RiskQuestion(BaseModel):
    """Model for a single risk assessment question."""
    question_id: str = Field(..., description="Unique identifier for the question")
    question_text: str = Field(..., description="The question text")
    options: list[dict] = Field(..., description="List of answer options with labels and scores")


class RiskQuestionnaire(BaseModel):
    """Complete risk assessment questionnaire."""
    questions: list[RiskQuestion] = Field(..., description="List of all risk questions")
    total_possible_score: int = Field(..., description="Maximum possible score")
    scoring_guide: dict = Field(..., description="Guide for interpreting scores")
