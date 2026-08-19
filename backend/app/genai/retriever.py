"""
Context retrieval for chatbot - fetches customer data to build LLM prompts.
"""

from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.db import crud
from app.data.data_loader import load_historical_data


def get_customer_context(customer_id: int, db: Session) -> Dict[str, Any]:
    """
    Fetch all relevant customer information for chatbot context.
    
    Retrieves:
    - Customer profile (income, expenses, assets, liabilities, net worth)
    - Risk assessment and risk category
    - Financial goals (all goals for this customer)
    - Generated plans (prefer selected plan if exists, otherwise all plans)
    - Historical asset return data
    
    Args:
        customer_id: ID of the customer
        db: Database session
        
    Returns:
        Dictionary containing all customer context for LLM prompt
        
    Raises:
        ValueError: If customer not found
    """
    # Fetch customer profile
    profile = crud.get_customer_profile(db, customer_id)
    if not profile:
        raise ValueError(f"Customer with ID {customer_id} not found")
    
    # Fetch latest risk assessment
    risk_assessment = crud.get_latest_risk_assessment(db, customer_id)
    
    # Fetch all goals for this customer
    goals = crud.get_customer_goals(db, customer_id)
    
    # Fetch plans - prefer active/selected plan, otherwise get all
    active_plan = crud.get_active_plan(db, customer_id)
    all_plans = crud.get_customer_plans(db, customer_id) if not active_plan else []
    
    # Load historical asset return data
    historical_data = load_historical_data()
    
    # Build context dictionary
    context = {
        "customer_id": customer_id,
        "profile": {
            "name": profile.name,
            "age": profile.age,
            "occupation": profile.occupation,
            "monthly_income": profile.monthly_income,
            "monthly_expenses": profile.monthly_expenses,
            "total_assets": profile.total_assets,
            "total_liabilities": profile.total_liabilities,
            "net_worth": profile.net_worth,
            "monthly_surplus": profile.monthly_surplus,
            "savings_rate": profile.savings_rate,
            "debt_to_income_ratio": profile.debt_to_income_ratio,
        },
        "risk_assessment": None,
        "goals": [],
        "plans": {
            "active_plan": None,
            "all_plans": []
        },
        "market_data": {
            "asset_classes": []
        }
    }
    
    # Add risk assessment if available
    if risk_assessment:
        context["risk_assessment"] = {
            "risk_score": risk_assessment.risk_score,
            "risk_category": risk_assessment.risk_category,
            "answers": risk_assessment.answers,
            "assessed_at": risk_assessment.created_at.isoformat() if risk_assessment.created_at else None
        }
    
    # Add goals
    for goal in goals:
        context["goals"].append({
            "goal_id": goal.id,
            "goal_name": goal.goal_name,
            "goal_type": goal.goal_type,
            "target_amount": goal.target_amount,
            "current_savings": goal.current_savings,
            "time_horizon_years": goal.time_horizon_years,
            "priority": goal.priority,
            "required_monthly_savings": goal.required_monthly_saving,
            "is_achievable": goal.is_achievable,
        })
    
    # Add active plan if available
    if active_plan:
        context["plans"]["active_plan"] = _format_plan(active_plan)
    else:
        # If no active plan, include all plans
        context["plans"]["all_plans"] = [_format_plan(plan) for plan in all_plans]
    
    # Add historical market data
    for _, row in historical_data.iterrows():
        context["market_data"]["asset_classes"].append({
            "asset_category": row["asset_category"],
            "avg_annual_return": row["avg_annual_return"],
            "volatility": row["volatility"]
        })
    
    return context


def _format_plan(plan) -> Dict[str, Any]:
    """
    Format a plan object into a dictionary for context.
    
    Args:
        plan: PlanDB object
        
    Returns:
        Dictionary representation of the plan
    """
    # Plan data is stored in JSON fields, need to extract properly
    assumptions = plan.assumptions if hasattr(plan, 'assumptions') else {}
    asset_allocation = plan.asset_allocation if hasattr(plan, 'asset_allocation') else {}
    
    return {
        "plan_id": plan.id,
        "plan_name": plan.plan_name,
        "risk_level": assumptions.get("risk_level", "Unknown"),
        "allocation": asset_allocation,
        "blended_expected_return": assumptions.get("blended_expected_return", 0),
        "current_monthly_investment": plan.monthly_savings_target,
        "projected_corpus": assumptions.get("projected_corpus", 0),
        "gap_vs_target": assumptions.get("gap_vs_target", 0),
        "required_monthly_investment": assumptions.get(
            "required_monthly_investment", plan.monthly_savings_target
        ),
        "is_selected": plan.status == "active",
        "created_at": plan.created_at.isoformat() if plan.created_at else None
    }


def get_recent_chat_history(
    customer_id: int,
    session_id: str,
    db: Session,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Fetch recent chat messages for conversation context.
    
    Args:
        customer_id: ID of the customer
        session_id: Chat session ID
        db: Database session
        limit: Maximum number of messages to retrieve
        
    Returns:
        List of chat messages with role and content
    """
    messages = crud.get_recent_chat_messages(
        db=db,
        customer_id=customer_id,
        session_id=session_id,
        limit=limit
    )
    
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "role": msg.role,
            "content": msg.content,
            "timestamp": msg.created_at.isoformat() if msg.created_at else None
        })
    
    return formatted_messages
