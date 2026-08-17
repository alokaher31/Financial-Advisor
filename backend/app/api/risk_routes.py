"""
API routes for risk assessment management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.models import (
    RiskAssessment,
    RiskAssessmentCreate,
    RiskProfile,
    RiskQuestionnaire,
    RiskQuestion,
)
from app.core.risk_scoring import RISK_QUESTIONS
from app.utils.logger import logger

router = APIRouter(prefix="/risk", tags=["Risk Assessment"])


@router.get("/questionnaire", response_model=RiskQuestionnaire)
def get_risk_questionnaire():
    """
    Get the risk assessment questionnaire.
    
    Returns all questions with their options and scoring guide.
    """
    questions = []
    for q in RISK_QUESTIONS:
        questions.append(
            RiskQuestion(
                question_id=q.question_id,
                question_text=q.question_text,
                options=[
                    {"label": opt.label, "value": opt.value, "score": opt.score}
                    for opt in q.options
                ]
            )
        )
    
    return RiskQuestionnaire(
        questions=questions,
        total_possible_score=100,
        scoring_guide={
            "Conservative": "0-33 points - Low risk tolerance",
            "Moderate": "34-66 points - Moderate risk tolerance",
            "Aggressive": "67-100 points - High risk tolerance"
        }
    )


@router.post("/", response_model=RiskAssessment, status_code=status.HTTP_201_CREATED)
def create_risk_assessment(
    assessment: RiskAssessmentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new risk assessment.
    
    Automatically calculates:
    - Risk score (0-100)
    - Risk category (Conservative/Moderate/Aggressive)
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, assessment.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {assessment.customer_id} not found"
            )
        
        logger.info(f"Creating risk assessment for customer: {assessment.customer_id}")
        db_assessment = crud.create_risk_assessment(db, assessment)
        logger.info(
            f"Risk assessment created: Score={db_assessment.risk_score}, "
            f"Category={db_assessment.risk_category}"
        )
        return db_assessment
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating risk assessment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create risk assessment: {str(e)}"
        )


@router.get("/{assessment_id}", response_model=RiskAssessment)
def get_risk_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """Get a risk assessment by ID."""
    db_assessment = crud.get_risk_assessment(db, assessment_id)
    if not db_assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk assessment with ID {assessment_id} not found"
        )
    return db_assessment


@router.get("/customer/{customer_id}", response_model=List[RiskAssessment])
def get_customer_risk_assessments(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all risk assessments for a specific customer."""
    # Verify customer exists
    customer = crud.get_customer_profile(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    assessments = crud.get_customer_risk_assessments(db, customer_id, skip, limit)
    return assessments


@router.get("/customer/{customer_id}/latest", response_model=RiskAssessment)
def get_latest_risk_assessment(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get the most recent risk assessment for a customer."""
    assessment = crud.get_latest_risk_assessment(db, customer_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk assessment found for customer {customer_id}"
        )
    return assessment


@router.get("/customer/{customer_id}/profile", response_model=RiskProfile)
def get_risk_profile(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get comprehensive risk profile with investment recommendations.
    
    Based on the latest risk assessment, provides:
    - Asset allocation recommendations
    - Risk tolerance description
    - Investment recommendations
    """
    assessment = crud.get_latest_risk_assessment(db, customer_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk assessment found for customer {customer_id}"
        )
    
    # Calculate asset allocation based on risk category
    if assessment.risk_category == "Conservative":
        equity_pct = 30.0
        debt_pct = 60.0
        cash_pct = 10.0
        description = "Conservative investor preferring capital preservation over growth"
        recommendations = [
            "Focus on debt instruments like bonds and fixed deposits",
            "Consider liquid funds for emergency corpus",
            "Maintain 20-30% equity exposure for long-term goals",
            "Prefer large-cap equity funds over mid/small caps",
            "Consider gold as a hedge (5-10% allocation)"
        ]
    elif assessment.risk_category == "Moderate":
        equity_pct = 60.0
        debt_pct = 30.0
        cash_pct = 10.0
        description = "Balanced investor seeking moderate growth with manageable risk"
        recommendations = [
            "Balanced allocation between equity and debt",
            "Mix of large-cap and mid-cap equity funds",
            "Use debt funds for stability and tax efficiency",
            "Consider hybrid/balanced funds for diversification",
            "Rebalance portfolio annually"
        ]
    else:  # Aggressive
        equity_pct = 80.0
        debt_pct = 15.0
        cash_pct = 5.0
        description = "Aggressive investor comfortable with high volatility for growth"
        recommendations = [
            "Focus on equity investments for maximum growth",
            "Include mid-cap and small-cap exposure",
            "Consider sector-specific funds for higher returns",
            "Use debt primarily for emergency funds",
            "Long investment horizon recommended (10+ years)"
        ]
    
    profile = RiskProfile(
        risk_score=assessment.risk_score,
        risk_category=assessment.risk_category,
        equity_allocation=equity_pct,
        debt_allocation=debt_pct,
        cash_allocation=cash_pct,
        risk_tolerance_description=description,
        investment_recommendations=recommendations,
    )
    
    return profile


@router.delete("/{assessment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_risk_assessment(
    assessment_id: int,
    db: Session = Depends(get_db)
):
    """Delete a risk assessment."""
    success = crud.delete_risk_assessment(db, assessment_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Risk assessment with ID {assessment_id} not found"
        )
    logger.info(f"Risk assessment deleted: {assessment_id}")
    return None
