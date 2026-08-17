"""
CRUD (Create, Read, Update, Delete) operations for all database entities.
These functions handle database interactions and integrate with core financial logic.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime

from app.db.db_models import (
    CustomerProfileDB, GoalDB, PlanDB, 
    RiskAssessmentDB, ChatMessageDB
)
from app.models import (
    CustomerProfileCreate, CustomerProfileUpdate,
    GoalCreate, GoalUpdate,
    PlanCreate, PlanUpdate,
    RiskAssessmentCreate,
    ChatMessageCreate,
)
from app.core.net_worth_calculator import (
    calculate_net_worth, 
    calculate_monthly_surplus,
    calculate_debt_to_income_ratio
)
from app.core.goal_calculator import calculate_future_value
from app.core.risk_scoring import calculate_risk_score, classify_risk


# ============================================================================
# Customer Profile CRUD Operations
# ============================================================================

def create_customer_profile(db: Session, profile: CustomerProfileCreate) -> CustomerProfileDB:
    """
    Create a new customer profile with calculated financial metrics.
    
    Args:
        db: Database session
        profile: Customer profile data
        
    Returns:
        Created customer profile with calculated fields
    """
    # Calculate financial metrics
    net_worth = calculate_net_worth(profile.total_assets, profile.total_liabilities)
    monthly_surplus = calculate_monthly_surplus(profile.monthly_income, profile.monthly_expenses)
    debt_to_income = calculate_debt_to_income_ratio(profile.total_liabilities, profile.monthly_income)
    
    db_profile = CustomerProfileDB(
        name=profile.name,
        age=profile.age,
        occupation=profile.occupation,
        monthly_income=profile.monthly_income,
        monthly_expenses=profile.monthly_expenses,
        total_assets=profile.total_assets,
        total_liabilities=profile.total_liabilities,
        net_worth=net_worth,
        monthly_surplus=monthly_surplus,
        debt_to_income_ratio=debt_to_income,
    )
    
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def get_customer_profile(db: Session, customer_id: int) -> Optional[CustomerProfileDB]:
    """Get a customer profile by ID."""
    return db.query(CustomerProfileDB).filter(CustomerProfileDB.id == customer_id).first()


def get_customer_profiles(db: Session, skip: int = 0, limit: int = 100) -> List[CustomerProfileDB]:
    """Get all customer profiles with pagination."""
    return db.query(CustomerProfileDB).offset(skip).limit(limit).all()


def update_customer_profile(
    db: Session, 
    customer_id: int, 
    profile_update: CustomerProfileUpdate
) -> Optional[CustomerProfileDB]:
    """
    Update a customer profile and recalculate financial metrics.
    
    Args:
        db: Database session
        customer_id: ID of the customer to update
        profile_update: Updated profile data
        
    Returns:
        Updated customer profile or None if not found
    """
    db_profile = get_customer_profile(db, customer_id)
    if not db_profile:
        return None
    
    # Update fields that were provided
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)
    
    # Recalculate financial metrics
    db_profile.net_worth = calculate_net_worth(
        db_profile.total_assets, 
        db_profile.total_liabilities
    )
    db_profile.monthly_surplus = calculate_monthly_surplus(
        db_profile.monthly_income, 
        db_profile.monthly_expenses
    )
    db_profile.debt_to_income_ratio = calculate_debt_to_income_ratio(
        db_profile.total_liabilities, 
        db_profile.monthly_income
    )
    
    db.commit()
    db.refresh(db_profile)
    return db_profile


def delete_customer_profile(db: Session, customer_id: int) -> bool:
    """Delete a customer profile and all related data (cascade)."""
    db_profile = get_customer_profile(db, customer_id)
    if not db_profile:
        return False
    
    db.delete(db_profile)
    db.commit()
    return True


# ============================================================================
# Goal CRUD Operations
# ============================================================================

def create_goal(db: Session, goal: GoalCreate, return_rate: float = 0.06) -> GoalDB:
    """
    Create a new financial goal with required savings calculation.
    
    Args:
        db: Database session
        goal: Goal data
        return_rate: Expected annual return rate (default 6%)
        
    Returns:
        Created goal with calculated fields
    """
    # Calculate required monthly saving
    amount_needed = goal.target_amount - goal.current_savings
    
    # Use future value calculation to determine required monthly saving
    # We need to solve for monthly_contribution in the future value formula
    # For simplicity, using a basic calculation here
    months = goal.time_horizon_years * 12
    monthly_rate = return_rate / 12
    
    if monthly_rate > 0:
        # Future value of annuity formula solved for payment
        fv_factor = (pow(1 + monthly_rate, months) - 1) / monthly_rate
        required_monthly = amount_needed / fv_factor if fv_factor > 0 else amount_needed / months
    else:
        required_monthly = amount_needed / months if months > 0 else 0
    
    # Check if achievable based on customer's surplus
    customer = get_customer_profile(db, goal.customer_id)
    is_achievable = False
    if customer:
        is_achievable = required_monthly <= customer.monthly_surplus
    
    db_goal = GoalDB(
        customer_id=goal.customer_id,
        goal_type=goal.goal_type.value,
        goal_name=goal.goal_name,
        target_amount=goal.target_amount,
        current_savings=goal.current_savings,
        time_horizon_years=goal.time_horizon_years,
        priority=goal.priority.value,
        notes=goal.notes,
        required_monthly_saving=round(required_monthly, 2),
        is_achievable=is_achievable,
    )
    
    db.add(db_goal)
    db.commit()
    db.refresh(db_goal)
    return db_goal


def get_goal(db: Session, goal_id: int) -> Optional[GoalDB]:
    """Get a goal by ID."""
    return db.query(GoalDB).filter(GoalDB.id == goal_id).first()


def get_customer_goals(
    db: Session, 
    customer_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[GoalDB]:
    """Get all goals for a specific customer."""
    return db.query(GoalDB)\
        .filter(GoalDB.customer_id == customer_id)\
        .offset(skip)\
        .limit(limit)\
        .all()


def update_goal(db: Session, goal_id: int, goal_update: GoalUpdate) -> Optional[GoalDB]:
    """Update a goal and recalculate required savings."""
    db_goal = get_goal(db, goal_id)
    if not db_goal:
        return None
    
    # Update fields that were provided
    update_data = goal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, 'value'):  # Handle enum values
            setattr(db_goal, field, value.value)
        else:
            setattr(db_goal, field, value)
    
    # Recalculate required monthly saving
    amount_needed = db_goal.target_amount - db_goal.current_savings
    months = db_goal.time_horizon_years * 12
    return_rate = 0.06  # 6% annual return
    monthly_rate = return_rate / 12
    
    if monthly_rate > 0:
        fv_factor = (pow(1 + monthly_rate, months) - 1) / monthly_rate
        required_monthly = amount_needed / fv_factor if fv_factor > 0 else amount_needed / months
    else:
        required_monthly = amount_needed / months if months > 0 else 0
    
    db_goal.required_monthly_saving = round(required_monthly, 2)
    
    # Recalculate achievability
    customer = get_customer_profile(db, db_goal.customer_id)
    if customer:
        db_goal.is_achievable = required_monthly <= customer.monthly_surplus
    
    db.commit()
    db.refresh(db_goal)
    return db_goal


def delete_goal(db: Session, goal_id: int) -> bool:
    """Delete a goal."""
    db_goal = get_goal(db, goal_id)
    if not db_goal:
        return False
    
    db.delete(db_goal)
    db.commit()
    return True


# ============================================================================
# Plan CRUD Operations
# ============================================================================

def create_plan(db: Session, plan: PlanCreate) -> PlanDB:
    """Create a new financial plan."""
    db_plan = PlanDB(
        customer_id=plan.customer_id,
        plan_name=plan.plan_name,
        status=plan.status.value,
        asset_allocation=plan.asset_allocation.model_dump(),
        monthly_savings_target=plan.monthly_savings_target,
        goal_allocations=[ga.model_dump() for ga in plan.goal_allocations],
        monthly_breakdown=plan.monthly_breakdown.model_dump(),
        assumptions=plan.assumptions,
        notes=plan.notes,
    )
    
    db.add(db_plan)
    db.commit()
    db.refresh(db_plan)
    return db_plan


def get_plan(db: Session, plan_id: int) -> Optional[PlanDB]:
    """Get a plan by ID."""
    return db.query(PlanDB).filter(PlanDB.id == plan_id).first()


def get_customer_plans(
    db: Session, 
    customer_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[PlanDB]:
    """Get all plans for a specific customer."""
    return db.query(PlanDB)\
        .filter(PlanDB.customer_id == customer_id)\
        .order_by(desc(PlanDB.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_active_plan(db: Session, customer_id: int) -> Optional[PlanDB]:
    """Get the active plan for a customer."""
    return db.query(PlanDB)\
        .filter(and_(PlanDB.customer_id == customer_id, PlanDB.status == "active"))\
        .first()


def update_plan(db: Session, plan_id: int, plan_update: PlanUpdate) -> Optional[PlanDB]:
    """Update a plan."""
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return None
    
    # Update fields that were provided
    update_data = plan_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "status" and hasattr(value, 'value'):
            setattr(db_plan, field, value.value)
        else:
            setattr(db_plan, field, value)
    
    db.commit()
    db.refresh(db_plan)
    return db_plan


def delete_plan(db: Session, plan_id: int) -> bool:
    """Delete a plan."""
    db_plan = get_plan(db, plan_id)
    if not db_plan:
        return False
    
    db.delete(db_plan)
    db.commit()
    return True


# ============================================================================
# Risk Assessment CRUD Operations
# ============================================================================

def create_risk_assessment(db: Session, assessment: RiskAssessmentCreate) -> RiskAssessmentDB:
    """
    Create a new risk assessment with calculated risk score and category.
    
    Args:
        db: Database session
        assessment: Risk assessment data with questionnaire answers
        
    Returns:
        Created risk assessment with calculated fields
    """
    # Calculate risk score using the risk_scoring module
    risk_score = calculate_risk_score(assessment.answers)
    risk_category = classify_risk(risk_score)
    
    db_assessment = RiskAssessmentDB(
        customer_id=assessment.customer_id,
        risk_score=risk_score,
        risk_category=risk_category,
        answers=assessment.answers,
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


def get_risk_assessment(db: Session, assessment_id: int) -> Optional[RiskAssessmentDB]:
    """Get a risk assessment by ID."""
    return db.query(RiskAssessmentDB).filter(RiskAssessmentDB.id == assessment_id).first()


def get_customer_risk_assessments(
    db: Session, 
    customer_id: int, 
    skip: int = 0, 
    limit: int = 100
) -> List[RiskAssessmentDB]:
    """Get all risk assessments for a specific customer."""
    return db.query(RiskAssessmentDB)\
        .filter(RiskAssessmentDB.customer_id == customer_id)\
        .order_by(desc(RiskAssessmentDB.created_at))\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_latest_risk_assessment(db: Session, customer_id: int) -> Optional[RiskAssessmentDB]:
    """Get the most recent risk assessment for a customer."""
    return db.query(RiskAssessmentDB)\
        .filter(RiskAssessmentDB.customer_id == customer_id)\
        .order_by(desc(RiskAssessmentDB.created_at))\
        .first()


def delete_risk_assessment(db: Session, assessment_id: int) -> bool:
    """Delete a risk assessment."""
    db_assessment = get_risk_assessment(db, assessment_id)
    if not db_assessment:
        return False
    
    db.delete(db_assessment)
    db.commit()
    return True


# ============================================================================
# Chat Message CRUD Operations
# ============================================================================

def create_chat_message(db: Session, message: ChatMessageCreate) -> ChatMessageDB:
    """Create a new chat message."""
    db_message = ChatMessageDB(
        customer_id=message.customer_id,
        role=message.role.value,
        content=message.content,
        session_id=message.session_id,
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_chat_message(db: Session, message_id: int) -> Optional[ChatMessageDB]:
    """Get a chat message by ID."""
    return db.query(ChatMessageDB).filter(ChatMessageDB.id == message_id).first()


def get_chat_history(
    db: Session,
    customer_id: int,
    session_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[ChatMessageDB]:
    """
    Get chat history for a customer, optionally filtered by session.
    
    Args:
        db: Database session
        customer_id: ID of the customer
        session_id: Optional session ID to filter by
        skip: Number of messages to skip (for pagination)
        limit: Maximum number of messages to return
        
    Returns:
        List of chat messages ordered by creation time
    """
    query = db.query(ChatMessageDB).filter(ChatMessageDB.customer_id == customer_id)
    
    if session_id:
        query = query.filter(ChatMessageDB.session_id == session_id)
    
    return query.order_by(ChatMessageDB.created_at).offset(skip).limit(limit).all()


def get_recent_chat_messages(
    db: Session,
    customer_id: int,
    session_id: str,
    limit: int = 10
) -> List[ChatMessageDB]:
    """Get the most recent chat messages for context."""
    return db.query(ChatMessageDB)\
        .filter(and_(
            ChatMessageDB.customer_id == customer_id,
            ChatMessageDB.session_id == session_id
        ))\
        .order_by(desc(ChatMessageDB.created_at))\
        .limit(limit)\
        .all()


def delete_chat_session(db: Session, customer_id: int, session_id: str) -> bool:
    """Delete all messages in a chat session."""
    result = db.query(ChatMessageDB)\
        .filter(and_(
            ChatMessageDB.customer_id == customer_id,
            ChatMessageDB.session_id == session_id
        ))\
        .delete()
    
    db.commit()
    return result > 0


def get_customer_sessions(db: Session, customer_id: int) -> List[str]:
    """Get all unique session IDs for a customer."""
    sessions = db.query(ChatMessageDB.session_id)\
        .filter(ChatMessageDB.customer_id == customer_id)\
        .filter(ChatMessageDB.session_id.isnot(None))\
        .distinct()\
        .all()
    
    return [session[0] for session in sessions if session[0]]
