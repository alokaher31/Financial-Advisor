"""CRUD tests against the current database models and schemas."""

import pytest
from pydantic import ValidationError

from app.db import crud
from app.models import CustomerProfileCreate, CustomerProfileUpdate, GoalCreate, GoalUpdate


def _profile(name: str = "CRUD Test Customer") -> CustomerProfileCreate:
    return CustomerProfileCreate(
        name=name,
        age=32,
        occupation="Engineer",
        monthly_income=100_000,
        monthly_expenses=50_000,
        total_assets=500_000,
        total_liabilities=100_000,
    )


def test_customer_profile_crud_and_recalculation(db_session):
    created = crud.create_customer_profile(db_session, _profile())
    assert created.id is not None
    assert created.net_worth == 400_000
    assert created.savings_rate == pytest.approx(0.5)
    assert created.debt_to_income_ratio == pytest.approx(1 / 12)

    updated = crud.update_customer_profile(
        db_session,
        created.id,
        CustomerProfileUpdate(monthly_expenses=75_000),
    )
    assert updated.monthly_surplus == 25_000
    assert updated.savings_rate == pytest.approx(0.25)
    assert crud.delete_customer_profile(db_session, created.id) is True
    assert crud.get_customer_profile(db_session, created.id) is None


def test_partial_profile_update_validates_merged_state(db_session):
    created = crud.create_customer_profile(db_session, _profile())
    with pytest.raises(ValidationError, match="expenses"):
        crud.update_customer_profile(
            db_session,
            created.id,
            CustomerProfileUpdate(monthly_income=20_000),
        )


def test_goal_crud_uses_requested_return_assumption(db_session):
    customer = crud.create_customer_profile(db_session, _profile())
    goal = crud.create_goal(
        db_session,
        GoalCreate(
            customer_id=customer.id,
            goal_type="retirement",
            goal_name="Retirement",
            target_amount=1_000_000,
            current_savings=100_000,
            time_horizon_years=10,
            priority="high",
        ),
        return_rate=0.10,
    )
    original_required = goal.required_monthly_saving

    updated = crud.update_goal(
        db_session,
        goal.id,
        GoalUpdate(time_horizon_years=20),
        return_rate=0.10,
    )
    assert updated.required_monthly_saving < original_required
    assert crud.delete_goal(db_session, goal.id) is True
    assert crud.get_goal(db_session, goal.id) is None


def test_partial_goal_update_validates_current_savings_against_target(db_session):
    customer = crud.create_customer_profile(db_session, _profile())
    goal = crud.create_goal(
        db_session,
        GoalCreate(
            customer_id=customer.id,
            goal_type="other",
            goal_name="Goal",
            target_amount=1_000_000,
            current_savings=100_000,
            time_horizon_years=5,
        ),
    )
    with pytest.raises(ValidationError, match="cannot exceed"):
        crud.update_goal(
            db_session,
            goal.id,
            GoalUpdate(target_amount=50_000),
        )
