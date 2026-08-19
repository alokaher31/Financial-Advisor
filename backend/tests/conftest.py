"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.db.db_models import Base
from app.db.database import get_db
from app.config import get_settings
from app.core.risk_scoring import RISK_QUESTIONNAIRE

# Override settings for testing
settings = get_settings()

# Create test database engine (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test.
    Tables are created before the test and dropped after.
    """
    # Create all tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        # Drop all tables after test
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with a test database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    test_client = TestClient(app)
    try:
        register_response = test_client.post(
            "/api/v1/auth/register",
            json={
                "name": "API Test User",
                "email": "api-tests@example.com",
                "password": "testpass123",
            },
        )
        assert register_response.status_code == 201
        test_client.headers["Authorization"] = (
            f"Bearer {register_response.json()['access_token']}"
        )
        yield test_client
    finally:
        test_client.close()
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_customer_data():
    """Sample customer profile data for testing."""
    return {
        "name": "Test Customer",
        "age": 35,
        "occupation": "Software Engineer",
        "monthly_income": 150000.0,
        "monthly_expenses": 80000.0,
        "total_assets": 2500000.0,
        "total_liabilities": 500000.0,
    }


@pytest.fixture
def sample_goal_data():
    """Sample goal data for testing."""
    return {
        "goal_type": "retirement",
        "goal_name": "Retirement Fund",
        "target_amount": 20000000.0,
        "current_savings": 2000000.0,
        "time_horizon_years": 25,
        "priority": "high",
        "notes": "Want to retire comfortably at age 60",
    }


@pytest.fixture
def sample_risk_answers():
    """Sample risk assessment answers for testing."""
    return {question.id: question.options[2].id for question in RISK_QUESTIONNAIRE}
