"""
CRUD (Create, Read, Update, Delete) operations for all database entities.
These functions handle database interactions and integrate with core financial logic.
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_

from app.db.db_models import (
    UserDB, CustomerProfileDB, GoalDB, PlanDB,
    RiskAssessmentDB, ChatMessageDB
)
from app.models import (
    CustomerProfileBase, CustomerProfileCreate, CustomerProfileUpdate,
    GoalBase, GoalCreate, GoalUpdate,
    PlanCreate, PlanUpdate,
    RiskAssessmentCreate,
    ChatMessageCreate,
)
from app.core.net_worth_calculator import (
    calculate_net_worth,
    calculate_monthly_surplus,
    calculate_debt_to_income_ratio,
    calculate_savings_rate,
)
from app.core.goal_calculator import calculate_required_monthly_investment
from app.core.risk_scoring import calculate_risk_score, classify_risk


# ============================================================================
# User CRUD Operations (Authentication)
# ============================================================================

def create_user(db: Session, name: str, email: str, hashed_password: str) -> UserDB:
    """
    Create a new user account.
    
    Args:
        db: Database session
        name: User's full name
        email: User's email address
        hashed_password: Pre-hashed password
        
    Returns:
        Created user object
    """
    db_user = UserDB(
        name=name,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_id(db: Session, user_id: int) -> Optional[UserDB]:
    """
    Get a user by ID.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[UserDB]:
    """
    Get a user by email address.
    
    Args:
        db: Database session
        email: User's email address
        
    Returns:
        User object if found, None otherwise
    """
    return db.query(UserDB).filter(UserDB.email == email).first()


def update_user(db: Session, user_id: int, name: Optional[str] = None, email: Optional[str] = None) -> Optional[UserDB]:
    """
    Update user information.
    
    Args:
        db: Database session
        user_id: User ID
        name: New name (optional)
        email: New email (optional)
        
    Returns:
        Updated user object if found, None otherwise
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    if name is not None:
        db_user.name = name
    if email is not None:
        db_user.email = email
    
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user_password(db: Session, user_id: int, hashed_password: str) -> Optional[UserDB]:
    """
    Update user password.
    
    Args:
        db: Database session
        user_id: User ID
        hashed_password: New hashed password
        
    Returns:
        Updated user object if found, None otherwise
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return None
    
    db_user.hashed_password = hashed_password
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user account and all associated data.
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        True if user was deleted, False if not found
    """
    db_user = get_user_by_id(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


# ============================================================================
# Customer Profile CRUD Operations
# ============================================================================

def create_customer_profile(db: Session, profile: CustomerProfileCreate, user_id: Optional[int] = None) -> CustomerProfileDB:
    """
    Create a new customer profile with calculated financial metrics.

    Args:
        db: Database session
        profile: Customer profile data
        user_id: Optional user ID to link profile to authenticated user

    Returns:
        Created customer profile with calculated fields
    """
    net_worth = calculate_net_worth(profile.total_assets, profile.total_liabilities)
    monthly_surplus = calculate_monthly_surplus(profile.monthly_income, profile.monthly_expenses)
    debt_to_income = calculate_debt_to_income_ratio(profile.total_liabilities, profile.monthly_income)
    savings_rate = calculate_savings_rate(monthly_surplus, profile.monthly_income)

    db_profile = CustomerProfileDB(
        user_id=user_id,
        name=profile.name,
        age=profile.age,
        occupation=profile.occupation,
        monthly_income=profile.monthly_income,
        monthly_expenses=profile.monthly_expenses,
        total_assets=profile.total_assets,
        total_liabilities=profile.total_liabilities,
        net_worth=net_worth,
        monthly_surplus=monthly_surplus,
        savings_rate=savings_rate,
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


def get_user_customer_profiles(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[CustomerProfileDB]:
    """
    Get all customer profiles for a specific user.
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List of customer profiles belonging to the user
    """
    return db.query(CustomerProfileDB).filter(
        CustomerProfileDB.user_id == user_id
    ).offset(skip).limit(limit).all()


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

    update_data = profile_update.model_dump(exclude_unset=True)
    candidate = CustomerProfileBase.model_validate({
        "name": update_data.get("name", db_profile.name),
        "age": update_data.get("age", db_profile.age),
        "occupation": update_data.get("occupation", db_profile.occupation),
        "monthly_income": update_data.get("monthly_income", db_profile.monthly_income),
        "monthly_expenses": update_data.get("monthly_expenses", db_profile.monthly_expenses),
        "total_assets": update_data.get("total_assets", db_profile.total_assets),
        "total_liabilities": update_data.get("total_liabilities", db_profile.total_liabilities),
    })
    for field, value in candidate.model_dump().items():
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
    db_profile.savings_rate = calculate_savings_rate(
        db_profile.monthly_surplus,
        db_profile.monthly_income,
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
    required_monthly = calculate_required_monthly_investment(
        goal.target_amount,
        goal.current_savings,
        return_rate * 100,
        goal.time_horizon_years,
    )

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


def update_goal(
    db: Session,
    goal_id: int,
    goal_update: GoalUpdate,
    return_rate: float = 0.06,
) -> Optional[GoalDB]:
    """Update a goal and recalculate required savings."""
    db_goal = get_goal(db, goal_id)
    if not db_goal:
        return None

    update_data = goal_update.model_dump(exclude_unset=True)
    candidate = GoalBase.model_validate({
        "goal_type": update_data.get("goal_type", db_goal.goal_type),
        "goal_name": update_data.get("goal_name", db_goal.goal_name),
        "target_amount": update_data.get("target_amount", db_goal.target_amount),
        "current_savings": update_data.get("current_savings", db_goal.current_savings),
        "time_horizon_years": update_data.get("time_horizon_years", db_goal.time_horizon_years),
        "priority": update_data.get("priority", db_goal.priority),
        "notes": update_data.get("notes", db_goal.notes),
    })
    for field, value in candidate.model_dump().items():
        setattr(db_goal, field, value.value if hasattr(value, "value") else value)

    # Recalculate required monthly saving
    required_monthly = calculate_required_monthly_investment(
        db_goal.target_amount,
        db_goal.current_savings,
        return_rate * 100,
        db_goal.time_horizon_years,
    )

    db_goal.required_monthly_saving = round(required_monthly, 2)

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
