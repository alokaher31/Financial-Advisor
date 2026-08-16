"""
Seed the PostgreSQL database with synthetic demo customer data.

Data source:
    backend/app/data/synthetic_customers.csv

This data is synthetic/illustrative and is intended only
for prototype and demo purposes.
"""

from sqlalchemy import select

from app.data.data_loader import load_demo_customers
from app.db.database import Base, SessionLocal, engine
from app.db.db_models import Customer, Goal


def create_tables():
    """
    Create all database tables registered with SQLAlchemy.
    """

    Base.metadata.create_all(bind=engine)


def seed_customers():
    """
    Load synthetic customers and goals into PostgreSQL.

    The operation is idempotent:
    existing customers are not inserted again.
    """

    customers = load_demo_customers()

    db = SessionLocal()

    try:
        inserted_customers = 0
        inserted_goals = 0

        for customer_data in customers:

            # --------------------------------------------------
            # Check whether customer already exists
            # --------------------------------------------------

            existing_customer = db.scalar(
                select(Customer).where(
                    Customer.customer_name
                    == customer_data["customer_name"]
                )
            )

            if existing_customer:
                customer = existing_customer

            else:
                # ----------------------------------------------
                # Create Customer
                # ----------------------------------------------

                customer = Customer(
                    customer_name=customer_data["customer_name"],
                    age=customer_data["age"],
                    monthly_income=customer_data["monthly_income"],
                    monthly_expenses=customer_data["monthly_expenses"],
                    savings=customer_data["savings"],
                    total_assets=customer_data["total_assets"],
                    total_liabilities=customer_data[
                        "total_liabilities"
                    ],
                    likely_risk_category=customer_data[
                        "likely_risk_category"
                    ],
                )

                db.add(customer)

                # Flush so customer.id is generated
                db.flush()

                inserted_customers += 1

            # --------------------------------------------------
            # Check whether this customer's goal already exists
            # --------------------------------------------------

            existing_goal = db.scalar(
                select(Goal).where(
                    Goal.customer_id == customer.id,
                    Goal.goal_type
                    == customer_data["goal_type"],
                )
            )

            if not existing_goal:

                goal = Goal(
                    customer_id=customer.id,
                    goal_type=customer_data["goal_type"],
                    target_amount=customer_data["target_amount"],
                    current_goal_savings=customer_data[
                        "current_goal_savings"
                    ],
                    time_horizon_years=customer_data[
                        "time_horizon_years"
                    ],
                )

                db.add(goal)

                inserted_goals += 1

        db.commit()

        print(
            f"Seed completed successfully. "
            f"Customers inserted: {inserted_customers}, "
            f"Goals inserted: {inserted_goals}"
        )

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


def main():
    """
    Create database tables and seed synthetic demo data.
    """

    print("Creating database tables...")

    create_tables()

    print("Seeding synthetic customer data...")

    seed_customers()


if __name__ == "__main__":
    main()