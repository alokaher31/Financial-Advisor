from sqlalchemy import select

from app.db.crud import (
    create_customer,
    create_goal,
    delete_customer,
    delete_goal,
    get_customer,
    get_customer_by_name,
    get_customer_goals,
    get_customers,
    get_goal,
)
from app.db.database import SessionLocal
from app.db.db_models import Customer


def test_get_all_customers():
    """Verify that seeded customers can be retrieved."""

    db = SessionLocal()

    try:
        customers = get_customers(db)

        assert len(customers) == 8

    finally:
        db.close()


def test_get_customer_by_id():
    """Verify that a customer can be retrieved by ID."""

    db = SessionLocal()

    try:
        customer = get_customer(db, 1)

        assert customer is not None
        assert customer.id == 1

    finally:
        db.close()


def test_get_customer_by_name():
    """Verify that a customer can be retrieved by name."""

    db = SessionLocal()

    try:
        customers = get_customers(db)

        assert len(customers) > 0

        expected_name = customers[0].customer_name

        customer = get_customer_by_name(
            db,
            expected_name,
        )

        assert customer is not None
        assert customer.customer_name == expected_name

    finally:
        db.close()


def test_get_customer_goals():
    """Verify that customer goals can be retrieved."""

    db = SessionLocal()

    try:
        customers = get_customers(db)

        customer = customers[0]

        goals = get_customer_goals(
            db,
            customer.id,
        )

        assert len(goals) >= 1

        for goal in goals:
            assert goal.customer_id == customer.id

    finally:
        db.close()


def test_create_and_delete_customer():
    """Verify customer creation and deletion."""

    db = SessionLocal()

    test_name = "CRUD Test Customer"

    try:
        # Remove leftover test customer if it exists
        existing = get_customer_by_name(
            db,
            test_name,
        )

        if existing:
            delete_customer(
                db,
                existing.id,
            )

        customer_data = {
            "customer_name": test_name,
            "age": 32,
            "monthly_income": 100000.0,
            "monthly_expenses": 50000.0,
            "savings": 200000.0,
            "total_assets": 500000.0,
            "total_liabilities": 100000.0,
            "likely_risk_category": "Moderate",
        }

        customer = create_customer(
            db,
            customer_data,
        )

        assert customer.id is not None
        assert customer.customer_name == test_name

        fetched = get_customer(
            db,
            customer.id,
        )

        assert fetched is not None
        assert fetched.customer_name == test_name

        deleted = delete_customer(
            db,
            customer.id,
        )

        assert deleted is True

        assert get_customer(
            db,
            customer.id,
        ) is None

    finally:
        # Safety cleanup
        leftover = get_customer_by_name(
            db,
            test_name,
        )

        if leftover:
            delete_customer(
                db,
                leftover.id,
            )

        db.close()


def test_create_and_delete_goal():
    """Verify goal creation and deletion."""

    db = SessionLocal()

    try:
        customer = get_customers(db)[0]

        goal_data = {
            "goal_type": "CRUD Test Goal",
            "target_amount": 1000000.0,
            "current_goal_savings": 100000.0,
            "time_horizon_years": 10,
        }

        goal = create_goal(
            db,
            customer.id,
            goal_data,
        )

        assert goal.id is not None
        assert goal.customer_id == customer.id
        assert goal.goal_type == "CRUD Test Goal"

        fetched = get_goal(
            db,
            goal.id,
        )

        assert fetched is not None
        assert fetched.goal_type == "CRUD Test Goal"

        deleted = delete_goal(
            db,
            goal.id,
        )

        assert deleted is True

        assert get_goal(
            db,
            goal.id,
        ) is None

    finally:
        db.close()