"""
Seed data for database initialization.
Provides sample customers, goals, risk assessments, and plans for testing and development.
"""

import logging
from sqlalchemy.orm import Session
from app.db.database import get_db_session, init_db
from app.db.crud import (
    create_customer_profile,
    create_goal,
    create_risk_assessment,
    get_customer_profiles,
)
from app.models import (
    CustomerProfileCreate,
    GoalCreate,
    GoalType,
    GoalPriority,
    RiskAssessmentCreate,
)

logger = logging.getLogger(__name__)


# Sample customer profiles
SAMPLE_CUSTOMERS = [
    {
        "name": "Rajesh Kumar",
        "age": 35,
        "occupation": "Software Engineer",
        "monthly_income": 150000.0,
        "monthly_expenses": 80000.0,
        "total_assets": 2500000.0,
        "total_liabilities": 500000.0,
    },
    {
        "name": "Priya Sharma",
        "age": 28,
        "occupation": "Marketing Manager",
        "monthly_income": 100000.0,
        "monthly_expenses": 55000.0,
        "total_assets": 1200000.0,
        "total_liabilities": 200000.0,
    },
    {
        "name": "Amit Patel",
        "age": 42,
        "occupation": "Business Owner",
        "monthly_income": 250000.0,
        "monthly_expenses": 150000.0,
        "total_assets": 8000000.0,
        "total_liabilities": 2000000.0,
    },
    {
        "name": "Sneha Reddy",
        "age": 25,
        "occupation": "Data Analyst",
        "monthly_income": 80000.0,
        "monthly_expenses": 50000.0,
        "total_assets": 500000.0,
        "total_liabilities": 100000.0,
    },
    {
        "name": "Vikram Singh",
        "age": 50,
        "occupation": "Senior Manager",
        "monthly_income": 200000.0,
        "monthly_expenses": 120000.0,
        "total_assets": 5000000.0,
        "total_liabilities": 800000.0,
    },
]


# Sample goals for each customer
SAMPLE_GOALS = {
    "Rajesh Kumar": [
        {
            "goal_type": GoalType.RETIREMENT,
            "goal_name": "Retirement Fund",
            "target_amount": 20000000.0,
            "current_savings": 2000000.0,
            "time_horizon_years": 25,
            "priority": GoalPriority.HIGH,
            "notes": "Want to retire comfortably at age 60",
        },
        {
            "goal_type": GoalType.EDUCATION,
            "goal_name": "Child's Higher Education",
            "target_amount": 3000000.0,
            "current_savings": 500000.0,
            "time_horizon_years": 10,
            "priority": GoalPriority.HIGH,
            "notes": "For daughter's college education",
        },
        {
            "goal_type": GoalType.HOME_PURCHASE,
            "goal_name": "Buy Apartment",
            "target_amount": 5000000.0,
            "current_savings": 1500000.0,
            "time_horizon_years": 5,
            "priority": GoalPriority.MEDIUM,
            "notes": "3 BHK apartment in Bangalore",
        },
    ],
    "Priya Sharma": [
        {
            "goal_type": GoalType.EMERGENCY_FUND,
            "goal_name": "Emergency Fund",
            "target_amount": 600000.0,
            "current_savings": 200000.0,
            "time_horizon_years": 2,
            "priority": GoalPriority.HIGH,
            "notes": "6 months of expenses as emergency fund",
        },
        {
            "goal_type": GoalType.VACATION,
            "goal_name": "Europe Trip",
            "target_amount": 400000.0,
            "current_savings": 100000.0,
            "time_horizon_years": 2,
            "priority": GoalPriority.LOW,
            "notes": "Dream vacation to Europe",
        },
        {
            "goal_type": GoalType.VEHICLE,
            "goal_name": "Buy Car",
            "target_amount": 1200000.0,
            "current_savings": 300000.0,
            "time_horizon_years": 3,
            "priority": GoalPriority.MEDIUM,
            "notes": "Mid-segment sedan",
        },
    ],
    "Amit Patel": [
        {
            "goal_type": GoalType.INVESTMENT,
            "goal_name": "Business Expansion",
            "target_amount": 10000000.0,
            "current_savings": 3000000.0,
            "time_horizon_years": 5,
            "priority": GoalPriority.HIGH,
            "notes": "Expand business to new locations",
        },
        {
            "goal_type": GoalType.RETIREMENT,
            "goal_name": "Early Retirement Fund",
            "target_amount": 30000000.0,
            "current_savings": 5000000.0,
            "time_horizon_years": 15,
            "priority": GoalPriority.HIGH,
            "notes": "Plan to retire at 55",
        },
    ],
    "Sneha Reddy": [
        {
            "goal_type": GoalType.EMERGENCY_FUND,
            "goal_name": "Emergency Fund",
            "target_amount": 300000.0,
            "current_savings": 100000.0,
            "time_horizon_years": 1,
            "priority": GoalPriority.HIGH,
            "notes": "Build emergency corpus",
        },
        {
            "goal_type": GoalType.EDUCATION,
            "goal_name": "MBA Abroad",
            "target_amount": 5000000.0,
            "current_savings": 400000.0,
            "time_horizon_years": 4,
            "priority": GoalPriority.MEDIUM,
            "notes": "Pursue MBA from top university",
        },
        {
            "goal_type": GoalType.DEBT_PAYOFF,
            "goal_name": "Clear Student Loan",
            "target_amount": 100000.0,
            "current_savings": 0.0,
            "time_horizon_years": 2,
            "priority": GoalPriority.HIGH,
            "notes": "Pay off remaining education loan",
        },
    ],
    "Vikram Singh": [
        {
            "goal_type": GoalType.RETIREMENT,
            "goal_name": "Retirement Planning",
            "target_amount": 25000000.0,
            "current_savings": 4200000.0,
            "time_horizon_years": 10,
            "priority": GoalPriority.HIGH,
            "notes": "Retirement at age 60",
        },
        {
            "goal_type": GoalType.EDUCATION,
            "goal_name": "Children's Education",
            "target_amount": 4000000.0,
            "current_savings": 800000.0,
            "time_horizon_years": 8,
            "priority": GoalPriority.HIGH,
            "notes": "For two children's college education",
        },
    ],
}


# Sample risk assessment answers
SAMPLE_RISK_ASSESSMENTS = {
    "Rajesh Kumar": {
        "age": "35-44",
        "investment_experience": "some",
        "time_horizon": "long",
        "market_reaction": "hold",
        "risk_comfort": "moderate",
        "goal_priority": "balanced",
        "income_stability": "stable",
        "emergency_fund": "yes",
        "debt_level": "low",
        "investment_knowledge": "moderate",
    },
    "Priya Sharma": {
        "age": "25-34",
        "investment_experience": "limited",
        "time_horizon": "medium",
        "market_reaction": "worried",
        "risk_comfort": "low",
        "goal_priority": "security",
        "income_stability": "stable",
        "emergency_fund": "partial",
        "debt_level": "low",
        "investment_knowledge": "basic",
    },
    "Amit Patel": {
        "age": "35-44",
        "investment_experience": "extensive",
        "time_horizon": "long",
        "market_reaction": "buy_more",
        "risk_comfort": "high",
        "goal_priority": "growth",
        "income_stability": "variable",
        "emergency_fund": "yes",
        "debt_level": "moderate",
        "investment_knowledge": "advanced",
    },
    "Sneha Reddy": {
        "age": "25-34",
        "investment_experience": "beginner",
        "time_horizon": "short",
        "market_reaction": "sell",
        "risk_comfort": "very_low",
        "goal_priority": "security",
        "income_stability": "stable",
        "emergency_fund": "no",
        "debt_level": "low",
        "investment_knowledge": "basic",
    },
    "Vikram Singh": {
        "age": "45-54",
        "investment_experience": "some",
        "time_horizon": "medium",
        "market_reaction": "hold",
        "risk_comfort": "moderate",
        "goal_priority": "balanced",
        "income_stability": "stable",
        "emergency_fund": "yes",
        "debt_level": "low",
        "investment_knowledge": "moderate",
    },
}


def seed_customers(db: Session) -> dict:
    """
    Seed customer profiles.

    Args:
        db: Database session

    Returns:
        Dictionary mapping customer names to their IDs
    """
    customer_ids = {}

    logger.info("Seeding customer profiles...")
    for customer_data in SAMPLE_CUSTOMERS:
        try:
            customer = CustomerProfileCreate(**customer_data)
            db_customer = create_customer_profile(db, customer)
            customer_ids[db_customer.name] = db_customer.id
            logger.info(f"Created customer: {db_customer.name} (ID: {db_customer.id})")
        except Exception as e:
            logger.error(f"Error creating customer {customer_data['name']}: {e}")

    return customer_ids


def seed_goals(db: Session, customer_ids: dict) -> None:
    """
    Seed financial goals for customers.

    Args:
        db: Database session
        customer_ids: Dictionary mapping customer names to their IDs
    """
    logger.info("Seeding financial goals...")

    for customer_name, goals_list in SAMPLE_GOALS.items():
        if customer_name not in customer_ids:
            logger.warning(f"Customer {customer_name} not found, skipping goals")
            continue

        customer_id = customer_ids[customer_name]

        for goal_data in goals_list:
            try:
                goal = GoalCreate(customer_id=customer_id, **goal_data)
                db_goal = create_goal(db, goal)
                logger.info(
                    f"Created goal: {db_goal.goal_name} for {customer_name} "
                    f"(Required monthly: ₹{db_goal.required_monthly_saving:,.2f})"
                )
            except Exception as e:
                logger.error(f"Error creating goal {goal_data['goal_name']}: {e}")


def seed_risk_assessments(db: Session, customer_ids: dict) -> None:
    """
    Seed risk assessments for customers.

    Args:
        db: Database session
        customer_ids: Dictionary mapping customer names to their IDs
    """
    logger.info("Seeding risk assessments...")

    for customer_name, answers in SAMPLE_RISK_ASSESSMENTS.items():
        if customer_name not in customer_ids:
            logger.warning(f"Customer {customer_name} not found, skipping risk assessment")
            continue

        customer_id = customer_ids[customer_name]

        try:
            assessment = RiskAssessmentCreate(
                customer_id=customer_id,
                answers=answers
            )
            db_assessment = create_risk_assessment(db, assessment)
            logger.info(
                f"Created risk assessment for {customer_name}: "
                f"Score={db_assessment.risk_score}, Category={db_assessment.risk_category}"
            )
        except Exception as e:
            logger.error(f"Error creating risk assessment for {customer_name}: {e}")


def seed_database() -> None:
    """
    Seed the database with sample data.
    This function initializes the database and populates it with test data.
    """
    logger.info("Starting database seeding...")

    # Initialize database (create tables)
    init_db()

    # Get database session
    db = get_db_session()

    try:
        # Check if database already has data
        existing_customers = get_customer_profiles(db, limit=1)
        if existing_customers:
            logger.info("Database already contains data. Skipping seed.")
            return

        # Seed customers
        customer_ids = seed_customers(db)

        # Seed goals
        seed_goals(db, customer_ids)

        # Seed risk assessments
        seed_risk_assessments(db, customer_ids)

        logger.info("Database seeding completed successfully!")
        logger.info(f"Created {len(customer_ids)} customers with goals and risk assessments")

    except Exception as e:
        logger.error(f"Error during database seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def clear_and_seed() -> None:
    """
    Clear all data and reseed the database.
    WARNING: This will delete all existing data!
    """
    from app.db.database import drop_tables

    logger.warning("Clearing all database data...")
    drop_tables()
    logger.info("Database cleared. Reseeding...")
    seed_database()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    seed_database()
