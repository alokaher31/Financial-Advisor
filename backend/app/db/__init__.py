"""
Database package for SQLAlchemy ORM models and session management.
"""

from .database import (
    engine,
    SessionLocal,
    get_db,
    get_db_session,
    create_tables,
    drop_tables,
    init_db,
    check_db_connection,
    DatabaseSession,
)

from .db_models import (
    Base,
    CustomerProfileDB,
    GoalDB,
    PlanDB,
    RiskAssessmentDB,
    ChatMessageDB,
)

__all__ = [
    # Database management
    "engine",
    "SessionLocal",
    "get_db",
    "get_db_session",
    "create_tables",
    "drop_tables",
    "init_db",
    "check_db_connection",
    "DatabaseSession",
    # ORM Models
    "Base",
    "CustomerProfileDB",
    "GoalDB",
    "PlanDB",
    "RiskAssessmentDB",
    "ChatMessageDB",
]
