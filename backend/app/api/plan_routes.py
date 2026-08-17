"""
API routes for financial plan management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import pandas as pd

from app.db.database import get_db
from app.db import crud
from app.models import (
    Plan,
    PlanCreate,
    PlanUpdate,
    PlanCreateRequest,
    AssetAllocation,
    MonthlyBreakdown,
    GoalAllocation,
)
from app.core.plan_generator import generate_plans
from app.data.data_loader import load_historical_data
from app.utils.logger import logger
from app.utils.exceptions import PlanGenerationException

router = APIRouter(prefix="/plans", tags=["Financial Plans"])


@router.post("/generate", response_model=List[dict], status_code=status.HTTP_200_OK)
def generate_financial_plans(
    request: PlanCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate 3 financial plans (Conservative, Balanced, Growth) for a customer.
    
    Uses deterministic calculations from core.plan_generator.
    Does NOT save plans to database - use POST /plans to save a specific plan.
    
    Returns:
        List of 3 plan dictionaries with allocations and projections
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, request.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {request.customer_id} not found"
            )
        
        # Verify goals exist
        if not request.goal_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="At least one goal ID is required"
            )
        
        goals = []
        for goal_id in request.goal_ids:
            goal = crud.get_goal(db, goal_id)
            if not goal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Goal with ID {goal_id} not found"
                )
            if goal.customer_id != request.customer_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Goal {goal_id} does not belong to customer {request.customer_id}"
                )
            goals.append(goal)
        
        # Get risk assessment (use latest if not specified)
        risk_assessment = None
        if request.risk_assessment_id:
            risk_assessment = crud.get_risk_assessment(db, request.risk_assessment_id)
            if not risk_assessment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Risk assessment with ID {request.risk_assessment_id} not found"
                )
        else:
            risk_assessment = crud.get_latest_risk_assessment(db, request.customer_id)
            if not risk_assessment:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"No risk assessment found for customer {request.customer_id}"
                )
        
        logger.info(f"Generating plans for customer {request.customer_id} with {len(goals)} goal(s)")
        
        # Prepare customer profile for plan generator
        customer_profile = {
            "monthly_income": customer.monthly_income,
            "monthly_expenses": customer.monthly_expenses,
        }
        
        # Use primary goal for plan generation (or combine if multiple)
        primary_goal = goals[0]  # Use first goal as primary
        goal_data = {
            "target_amount": primary_goal.target_amount,
            "current_amount": primary_goal.current_savings,
            "time_horizon_years": primary_goal.time_horizon_years,
        }
        
        # Load historical data
        try:
            historical_data = load_historical_data()
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            raise PlanGenerationException(
                "Failed to load historical market data",
                {"error": str(e)}
            )
        
        # Generate plans using core logic
        plans = generate_plans(
            customer_profile=customer_profile,
            risk_category=risk_assessment.risk_category,
            goal=goal_data,
            historical_data=historical_data
        )
        
        logger.info(f"Successfully generated {len(plans)} plans for customer {request.customer_id}")
        return plans
        
    except HTTPException:
        raise
    except PlanGenerationException:
        raise
    except Exception as e:
        logger.error(f"Error generating plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate plans: {str(e)}"
        )


@router.post("/", response_model=Plan, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan: PlanCreate,
    db: Session = Depends(get_db)
):
    """
    Save a generated plan to the database.
    
    Use this after calling /generate to persist a selected plan.
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, plan.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {plan.customer_id} not found"
            )
        
        logger.info(f"Creating plan '{plan.plan_name}' for customer: {plan.customer_id}")
        db_plan = crud.create_plan(db, plan)
        logger.info(f"Plan created with ID: {db_plan.id}")
        return db_plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create plan: {str(e)}"
        )


@router.get("/{plan_id}", response_model=Plan)
def get_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Get a plan by ID."""
    db_plan = crud.get_plan(db, plan_id)
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    return db_plan


@router.get("/customer/{customer_id}", response_model=List[Plan])
def get_customer_plans(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all plans for a specific customer."""
    # Verify customer exists
    customer = crud.get_customer_profile(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    plans = crud.get_customer_plans(db, customer_id, skip, limit)
    return plans


@router.get("/customer/{customer_id}/active", response_model=Plan)
def get_active_plan(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get the active plan for a customer."""
    plan = crud.get_active_plan(db, customer_id)
    if not plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No active plan found for customer {customer_id}"
        )
    return plan


@router.put("/{plan_id}", response_model=Plan)
def update_plan(
    plan_id: int,
    plan_update: PlanUpdate,
    db: Session = Depends(get_db)
):
    """Update a plan (e.g., change status, add notes)."""
    db_plan = crud.update_plan(db, plan_id, plan_update)
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    logger.info(f"Plan updated: {plan_id}")
    return db_plan


@router.post("/{plan_id}/select", response_model=Plan)
def select_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """
    Mark a plan as active/selected.
    
    Deactivates any other active plans for the same customer.
    """
    db_plan = crud.get_plan(db, plan_id)
    if not db_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    
    # Deactivate other active plans for this customer
    active_plan = crud.get_active_plan(db, db_plan.customer_id)
    if active_plan and active_plan.id != plan_id:
        crud.update_plan(db, active_plan.id, PlanUpdate(status="archived"))
    
    # Activate this plan
    from app.models import PlanStatus
    updated_plan = crud.update_plan(db, plan_id, PlanUpdate(status=PlanStatus.ACTIVE))
    
    logger.info(f"Plan {plan_id} selected as active for customer {db_plan.customer_id}")
    return updated_plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(
    plan_id: int,
    db: Session = Depends(get_db)
):
    """Delete a plan."""
    success = crud.delete_plan(db, plan_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan with ID {plan_id} not found"
        )
    logger.info(f"Plan deleted: {plan_id}")
    return None
