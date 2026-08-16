"""
CRUD operations for Customer and Goal records.

CRUD = Create, Read, Update, Delete
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.db_models import Customer, Goal


# ============================================================
# Customer CRUD
# ============================================================

def get_customer(
    db: Session,
    customer_id: int,
):
    """Get one customer by ID."""

    return db.get(Customer, customer_id)


def get_customer_by_name(
    db: Session,
    customer_name: str,
):
    """Get one customer by name."""

    return db.scalar(
        select(Customer).where(
            Customer.customer_name == customer_name
        )
    )


def get_customers(
    db: Session,
):
    """Get all customers."""

    return db.scalars(
        select(Customer)
    ).all()


def create_customer(
    db: Session,
    customer_data: dict,
):
    """Create a new customer."""

    customer = Customer(
        customer_name=customer_data["customer_name"],
        age=customer_data["age"],
        monthly_income=customer_data["monthly_income"],
        monthly_expenses=customer_data["monthly_expenses"],
        savings=customer_data.get("savings", 0.0),
        total_assets=customer_data.get("total_assets", 0.0),
        total_liabilities=customer_data.get(
            "total_liabilities",
            0.0,
        ),
        likely_risk_category=customer_data[
            "likely_risk_category"
        ],
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_id: int,
):
    """Delete a customer by ID."""

    customer = db.get(Customer, customer_id)

    if customer is None:
        return False

    db.delete(customer)
    db.commit()

    return True


# ============================================================
# Goal CRUD
# ============================================================

def get_goal(
    db: Session,
    goal_id: int,
):
    """Get one goal by ID."""

    return db.get(Goal, goal_id)


def get_customer_goals(
    db: Session,
    customer_id: int,
):
    """Get all goals belonging to a customer."""

    return db.scalars(
        select(Goal).where(
            Goal.customer_id == customer_id
        )
    ).all()


def create_goal(
    db: Session,
    customer_id: int,
    goal_data: dict,
):
    """Create a new financial goal for a customer."""

    goal = Goal(
        customer_id=customer_id,
        goal_type=goal_data["goal_type"],
        target_amount=goal_data["target_amount"],
        current_goal_savings=goal_data.get(
            "current_goal_savings",
            0.0,
        ),
        time_horizon_years=goal_data[
            "time_horizon_years"
        ],
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    return goal


def delete_goal(
    db: Session,
    goal_id: int,
):
    """Delete a goal by ID."""

    goal = db.get(Goal, goal_id)

    if goal is None:
        return False

    db.delete(goal)
    db.commit()

    return True