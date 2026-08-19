"""Seed-data tests against an isolated database."""

from sqlalchemy import func, select

from app.db.db_models import CustomerProfileDB, GoalDB, RiskAssessmentDB
from app.db.seed_data import (
    SAMPLE_CUSTOMERS,
    SAMPLE_GOALS,
    seed_customers,
    seed_goals,
    seed_risk_assessments,
)


def test_seed_data_is_complete_and_valid(db_session):
    customer_ids = seed_customers(db_session)
    seed_goals(db_session, customer_ids)
    seed_risk_assessments(db_session, customer_ids)

    customer_count = db_session.scalar(
        select(func.count()).select_from(CustomerProfileDB)
    )
    goal_count = db_session.scalar(select(func.count()).select_from(GoalDB))
    assessment_count = db_session.scalar(
        select(func.count()).select_from(RiskAssessmentDB)
    )

    assert customer_count == len(SAMPLE_CUSTOMERS)
    assert goal_count == sum(len(goals) for goals in SAMPLE_GOALS.values())
    assert assessment_count == len(SAMPLE_CUSTOMERS)

    customers = db_session.scalars(select(CustomerProfileDB)).all()
    assert all(customer.goals for customer in customers)
    assert all(customer.risk_assessments for customer in customers)
