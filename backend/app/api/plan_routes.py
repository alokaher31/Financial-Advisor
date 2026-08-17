"""
API routes for financial plan management.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import pandas as pd

from app.db.database import get_db
from app.db import crud
from app.models import (
    Plan,
    PlanCreate,
    PlanUpdate,
    PlanCreateRequest,
    PlanStatus,
    AssetAllocation,
    MonthlyBreakdown,
    GoalAllocation,
)
from app.core.plan_generator import generate_plans
from app.data.data_loader import load_historical_data
from app.utils.logger import logger
from app.utils.exceptions import PlanGenerationException

router = APIRouter(prefix="/plans", tags=["Financial Plans"])


# ---------------------------------------------------------------------------
# Request models for new endpoints
# ---------------------------------------------------------------------------

class PlanCompareRequest(BaseModel):
    """Request body for comparing plans."""
    customer_id: int = Field(..., gt=0)
    plan_ids: List[int] = Field(..., min_length=2, description="IDs of plans to compare")


class WhatIfScenarioInput(BaseModel):
    """The hypothetical change to evaluate."""
    type: str = Field(..., description="e.g. 'extra_monthly_investment'")
    amount: float = Field(..., description="Adjustment amount")


class WhatIfRequest(BaseModel):
    """Request body for what-if analysis."""
    customer_id: int = Field(..., gt=0)
    goal_id: int = Field(..., gt=0)
    plan_id: int = Field(..., gt=0)
    scenario: WhatIfScenarioInput


# ---------------------------------------------------------------------------
# Helper: persist generated plans to DB
# ---------------------------------------------------------------------------

def _persist_generated_plans(
    db: Session,
    generated_plans: list[dict],
    customer,
    goals: list,
    risk_assessment,
) -> list[dict]:
    """
    Persist each generated plan dict via crud.create_plan() and return the
    original dicts enriched with the real DB ``id``.
    """
    primary_goal = goals[0]
    persisted = []

    for plan_dict in generated_plans:
        # Map the generated allocation dict to AssetAllocation model
        alloc = plan_dict.get("allocation", {})
        asset_allocation = AssetAllocation(
            equity_percentage=float(alloc.get("Equity", 0)),
            debt_percentage=float(alloc.get("Debt", 0)),
            cash_percentage=float(alloc.get("Cash", 0)),
        )

        goal_allocation = GoalAllocation(
            goal_id=primary_goal.id,
            goal_name=primary_goal.goal_name,
            monthly_allocation=float(plan_dict.get("required_monthly_investment", 0)),
            priority_rank=1,
        )

        surplus = customer.monthly_income - customer.monthly_expenses
        monthly_breakdown = MonthlyBreakdown(
            total_income=customer.monthly_income,
            total_expenses=customer.monthly_expenses,
            available_for_savings=max(surplus, 0),
            allocated_to_goals=float(plan_dict.get("required_monthly_investment", 0)),
            emergency_fund_contribution=0,
            discretionary_savings=max(surplus - float(plan_dict.get("required_monthly_investment", 0)), 0),
            surplus_deficit=surplus - float(plan_dict.get("required_monthly_investment", 0)),
        )

        plan_create = PlanCreate(
            customer_id=customer.id,
            plan_name=plan_dict["plan_name"],
            status=PlanStatus.DRAFT,
            asset_allocation=asset_allocation,
            monthly_savings_target=float(plan_dict.get("required_monthly_investment", 0)),
            goal_allocations=[goal_allocation],
            monthly_breakdown=monthly_breakdown,
            assumptions={
                "risk_category": risk_assessment.risk_category,
                "blended_expected_return": plan_dict.get("blended_expected_return"),
                "projected_corpus": plan_dict.get("projected_corpus"),
                "gap_vs_target": plan_dict.get("gap_vs_target"),
                "risk_level": plan_dict.get("risk_level"),
                "time_horizon_years": primary_goal.time_horizon_years,
                "target_amount": primary_goal.target_amount,
                "current_savings": primary_goal.current_savings,
            },
        )

        db_plan = crud.create_plan(db, plan_create)

        # Enrich original dict with the real DB id
        enriched = dict(plan_dict)
        enriched["id"] = db_plan.id
        persisted.append(enriched)

    return persisted


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/generate", status_code=status.HTTP_200_OK)
def generate_financial_plans(
    request: PlanCreateRequest,
    db: Session = Depends(get_db)
):
    """
    Generate 3 financial plans (Conservative, Balanced, Growth) for a customer.

    Plans are automatically persisted to the database so the returned objects
    include real ``id`` fields usable with ``POST /plans/{id}/select``.
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

        # Use primary goal for plan generation
        primary_goal = goals[0]
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

        # Persist all 3 plans and return with DB IDs
        persisted_plans = _persist_generated_plans(
            db, plans, customer, goals, risk_assessment
        )

        logger.info(f"Successfully generated and persisted {len(persisted_plans)} plans for customer {request.customer_id}")
        return persisted_plans

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


@router.post("/compare", status_code=status.HTTP_200_OK)
def compare_financial_plans(
    request: PlanCompareRequest,
    db: Session = Depends(get_db)
):
    """
    Compare multiple financial plans side-by-side.

    Attempts to use the GenAI comparator for a natural-language summary.
    Falls back to a deterministic comparison if the LLM is unavailable.
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, request.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {request.customer_id} not found"
            )

        # Load the plans from DB
        plans_data = []
        for pid in request.plan_ids:
            db_plan = crud.get_plan(db, pid)
            if not db_plan:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Plan with ID {pid} not found"
                )
            if db_plan.customer_id != request.customer_id:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Plan {pid} does not belong to customer {request.customer_id}"
                )
            # Reconstruct the dict format expected by the comparator
            alloc_json = db_plan.asset_allocation if isinstance(db_plan.asset_allocation, dict) else {}
            assumptions = db_plan.assumptions if isinstance(db_plan.assumptions, dict) else {}
            plans_data.append({
                "plan_name": db_plan.plan_name,
                "allocation": {
                    "Equity": alloc_json.get("equity_percentage", 0),
                    "Debt": alloc_json.get("debt_percentage", 0),
                    "Cash": alloc_json.get("cash_percentage", 0),
                },
                "blended_expected_return": assumptions.get("blended_expected_return", 0),
                "projected_corpus": assumptions.get("projected_corpus", 0),
                "gap_vs_target": assumptions.get("gap_vs_target", 0),
                "required_monthly_investment": db_plan.monthly_savings_target,
                "risk_level": assumptions.get("risk_category", db_plan.plan_name),
            })

        # Try GenAI comparison, fall back to deterministic
        summary = _deterministic_comparison(plans_data)
        try:
            from app.genai.comparator import compare_plans as genai_compare
            if len(plans_data) == 3:
                summary = genai_compare(plans_data)
        except Exception as llm_err:
            logger.warning(f"GenAI comparison unavailable, using deterministic fallback: {llm_err}")

        # Key differences
        key_differences = []
        if len(plans_data) >= 2:
            returns = [p.get("blended_expected_return", 0) for p in plans_data]
            investments = [p.get("required_monthly_investment", 0) for p in plans_data]
            key_differences.append(
                f"Expected returns range from {min(returns):.2f}% to {max(returns):.2f}%"
            )
            key_differences.append(
                f"Required monthly investment ranges from ₹{min(investments):,.0f} to ₹{max(investments):,.0f}"
            )

        return {
            "summary": summary,
            "plans": plans_data,
            "key_differences": key_differences,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing plans: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to compare plans: {str(e)}"
        )


@router.post("/whatif", status_code=status.HTTP_200_OK)
def whatif_analysis(
    request: WhatIfRequest,
    db: Session = Depends(get_db)
):
    """
    Run a What-If scenario analysis.

    Recalculates plan projections with adjusted parameters and returns
    a before/after comparison with an explanation.
    """
    try:
        # Verify customer exists
        customer = crud.get_customer_profile(db, request.customer_id)
        if not customer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Customer with ID {request.customer_id} not found"
            )

        # Verify goal exists
        goal = crud.get_goal(db, request.goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal with ID {request.goal_id} not found"
            )

        # Verify plan exists
        db_plan = crud.get_plan(db, request.plan_id)
        if not db_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Plan with ID {request.plan_id} not found"
            )

        # Reconstruct inputs for the whatif calculator
        customer_profile = {
            "monthly_income": customer.monthly_income,
            "monthly_expenses": customer.monthly_expenses,
        }
        goal_data = {
            "target_amount": goal.target_amount,
            "current_amount": goal.current_savings,
            "time_horizon_years": goal.time_horizon_years,
        }

        # Get risk assessment
        risk_assessment = crud.get_latest_risk_assessment(db, request.customer_id)
        risk_category = risk_assessment.risk_category if risk_assessment else "Moderate"

        # Load historical data
        historical_data = load_historical_data()

        # Map scenario type to whatif_analyzer parameter
        scenario = request.scenario
        if scenario.type == "extra_monthly_investment":
            # Calculate adjusted monthly expenses (lower expenses = more investment)
            adjustment_parameter = "monthly_expenses"
            adjusted_value = customer.monthly_expenses - scenario.amount
            if adjusted_value < 0:
                adjusted_value = 0
        elif scenario.type in ("monthly_income", "monthly_expenses", "time_horizon_years",
                               "current_amount", "target_amount"):
            adjustment_parameter = scenario.type
            adjusted_value = scenario.amount
        else:
            # Default: treat as extra investment by reducing expenses
            adjustment_parameter = "monthly_expenses"
            adjusted_value = max(customer.monthly_expenses - scenario.amount, 0)

        # Use the whatif calculator
        from app.genai.whatif_analyzer import calculate_whatif_scenario
        whatif_result = calculate_whatif_scenario(
            customer_profile=customer_profile,
            goal=goal_data,
            risk_category=risk_category,
            historical_data=historical_data,
            adjustment_parameter=adjustment_parameter,
            adjusted_value=adjusted_value,
            plan_name=db_plan.plan_name,
        )

        base = whatif_result.get("base_plan", {})
        adjusted = whatif_result.get("adjusted_plan", {})
        impact = whatif_result.get("impact", {})

        # Try to generate narration
        explanation = (
            f"By adjusting {scenario.type} by ₹{scenario.amount:,.0f}, your projected corpus "
            f"changes by ₹{impact.get('corpus_change', 0):,.0f}."
        )
        try:
            from app.genai.whatif_analyzer import narrate_whatif_scenario
            explanation = narrate_whatif_scenario(whatif_result)
        except Exception as llm_err:
            logger.warning(f"GenAI narration unavailable, using deterministic fallback: {llm_err}")

        return {
            "before": {
                "monthly_investment": base.get("required_monthly_investment", 0),
                "projected_corpus": base.get("projected_corpus", 0),
                "gap_vs_target": base.get("gap_vs_target", 0),
            },
            "after": {
                "monthly_investment": adjusted.get("required_monthly_investment", 0),
                "projected_corpus": adjusted.get("projected_corpus", 0),
                "gap_vs_target": adjusted.get("gap_vs_target", 0),
            },
            "change": {
                "corpus_change": impact.get("corpus_change", 0),
                "gap_change": impact.get("gap_change", 0),
                "investment_change": impact.get("investment_change", 0),
            },
            "explanation": explanation,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error running what-if analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to run what-if analysis: {str(e)}"
        )


# ---------------------------------------------------------------------------
# Helper: deterministic plan comparison (no LLM needed)
# ---------------------------------------------------------------------------

def _deterministic_comparison(plans: list[dict]) -> str:
    """Build a plain-text comparison from plan metrics."""
    if not plans:
        return "No plans to compare."

    lines = ["Here is a side-by-side comparison of your plans:\n"]
    for p in plans:
        name = p.get("plan_name", "Unknown")
        ret = p.get("blended_expected_return", 0)
        inv = p.get("required_monthly_investment", 0)
        risk = p.get("risk_level", "Unknown")
        lines.append(
            f"• {name} ({risk} risk): {ret:.2f}% expected return, "
            f"₹{inv:,.0f}/month required investment"
        )

    # Simple recommendation
    sorted_plans = sorted(plans, key=lambda p: p.get("projected_corpus", 0), reverse=True)
    best = sorted_plans[0].get("plan_name", "Unknown")
    lines.append(f"\nThe {best} plan offers the highest projected corpus, "
                 f"but carries more risk. Choose based on your comfort level.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Existing CRUD endpoints (unchanged)
# ---------------------------------------------------------------------------

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
