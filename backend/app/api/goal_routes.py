"""
API routes for financial goal management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.models import (
    Goal,
    GoalCreate,
    GoalUpdate,
    GoalCalculation,
)
from app.config import get_settings
from app.utils.logger import logger

router = APIRouter(prefix="/goal", tags=["Financial Goals"])
settings = get_settings()


@router.post("/", response_model=Goal, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new financial goal.
    
    Automatically calculates:
    - Required monthly savings
    - Achievability based on customer's surplus
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, goal.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {goal.customer_id} not found"
            )
        
        logger.info(f"Creating goal '{goal.goal_name}' for customer: {goal.customer_id}")
        
        # Use appropriate return rate based on goal type
        return_rate = settings.DEFAULT_EQUITY_RETURN  # 12% for equity-based goals
        if goal.goal_type.value in ["emergency_fund", "debt_payoff"]:
            return_rate = settings.DEFAULT_SAVINGS_RATE  # 5% for conservative goals
        
        db_goal = crud.create_goal(db, goal, return_rate=return_rate)
        logger.info(
            f"Goal created: {db_goal.goal_name} (ID: {db_goal.id}), "
            f"Required monthly: ₹{db_goal.required_monthly_saving:,.2f}"
        )
        return db_goal
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create goal: {str(e)}"
        )


@router.get("/{goal_id}", response_model=Goal)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Get a goal by ID."""
    db_goal = crud.get_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    return db_goal


@router.get("/customer/{customer_id}", response_model=List[Goal])
def get_customer_goals(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all goals for a specific customer."""
    # Verify customer exists
    customer = crud.get_customer_profile(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer with ID {customer_id} not found"
        )
    
    goals = crud.get_customer_goals(db, customer_id, skip, limit)
    return goals


@router.put("/{goal_id}", response_model=Goal)
def update_goal(
    goal_id: int,
    goal_update: GoalUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a goal.
    
    Automatically recalculates required savings and achievability.
    """
    db_goal = crud.update_goal(db, goal_id, goal_update)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    logger.info(f"Goal updated: {goal_id}")
    return db_goal


@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """Delete a goal."""
    success = crud.delete_goal(db, goal_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    logger.info(f"Goal deleted: {goal_id}")
    return None


@router.get("/{goal_id}/calculation", response_model=GoalCalculation)
def get_goal_calculation(
    goal_id: int,
    db: Session = Depends(get_db)
):
    """
    Get detailed calculation breakdown for a goal.
    
    Shows:
    - Amount needed
    - Required monthly/annual savings
    - Achievability analysis
    - Assumed return rate
    """
    db_goal = crud.get_goal(db, goal_id)
    if not db_goal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {goal_id} not found"
        )
    
    customer = crud.get_customer_profile(db, db_goal.customer_id)
    amount_needed = db_goal.target_amount - db_goal.current_savings
    
    # Determine return rate based on goal type
    return_rate = settings.DEFAULT_EQUITY_RETURN
    if db_goal.goal_type in ["emergency_fund", "debt_payoff"]:
        return_rate = settings.DEFAULT_SAVINGS_RATE
    
    # Calculate achievability percentage
    achievability_pct = 0.0
    if customer and customer.monthly_surplus > 0:
        achievability_pct = min(
            (customer.monthly_surplus / db_goal.required_monthly_saving) * 100,
            100.0
        ) if db_goal.required_monthly_saving > 0 else 100.0
    
    calculation = GoalCalculation(
        goal_id=db_goal.id,
        goal_name=db_goal.goal_name,
        target_amount=db_goal.target_amount,
        current_savings=db_goal.current_savings,
        amount_needed=amount_needed,
        time_horizon_years=db_goal.time_horizon_years,
        required_monthly_saving=db_goal.required_monthly_saving,
        required_annual_saving=db_goal.required_monthly_saving * 12,
        total_savings_required=db_goal.required_monthly_saving * db_goal.time_horizon_years * 12,
        assumed_return_rate=return_rate,
        is_achievable=db_goal.is_achievable,
        achievability_percentage=round(achievability_pct, 2),
    )
    
    return calculation
