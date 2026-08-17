from sqlalchemy import func, select

from app.db.database import SessionLocal
from app.db.db_models import Customer, Goal


def test_customer_count():
    """Database should contain exactly 8 seeded customers."""

    db = SessionLocal()

    try:
        count = db.scalar(
            select(func.count()).select_from(Customer)
        )

        assert count == 8

    finally:
        db.close()


def test_goal_count():
    """Database should contain exactly 8 seeded goals."""

    db = SessionLocal()

    try:
        count = db.scalar(
            select(func.count()).select_from(Goal)
        )

        assert count == 8

    finally:
        db.close()


def test_customers_have_goals():
    """Every seeded customer should have at least one goal."""

    db = SessionLocal()

    try:
        customers = db.scalars(
            select(Customer)
        ).all()

        assert len(customers) == 8

        for customer in customers:
            assert len(customer.goals) >= 1

    finally:
        db.close()