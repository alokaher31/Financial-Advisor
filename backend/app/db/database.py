"""
Database connection and session management.
Provides SQLAlchemy engine, session factory, and dependency injection for FastAPI.
Supports both SQLite (default) and PostgreSQL.
"""

import os
import logging
from pathlib import Path
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from sqlalchemy.pool import StaticPool

# ---------------------------------------------------------
# Load backend/.env if present
# ---------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_ROOT / ".env")

logger = logging.getLogger(__name__)

# ---------------------------------------------------------
# Resolve DATABASE_URL
# ---------------------------------------------------------

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./financial_advisor.db")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# ---------------------------------------------------------
# Create engine (SQLite vs PostgreSQL)
# ---------------------------------------------------------

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=DB_ECHO,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

else:
    # PostgreSQL or other database
    engine = create_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )

# ---------------------------------------------------------
# Session factory & ORM base
# ---------------------------------------------------------

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ---------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------

def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.

    Usage in FastAPI route:
    ```
    @app.get("/items")
    def read_items(db: Session = Depends(get_db)):
        items = db.query(Item).all()
        return items
    ```

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a database session for use outside of FastAPI dependency injection.

    Returns:
        Session: SQLAlchemy database session
    """
    return SessionLocal()


def create_tables():
    """
    Create all database tables.
    Should be called on application startup.
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def drop_tables():
    """
    Drop all database tables.
    USE WITH CAUTION - This will delete all data!
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Database tables dropped successfully")
    except Exception as e:
        logger.error(f"Error dropping database tables: {e}")
        raise


def init_db():
    """
    Initialize database: create tables.
    """
    logger.info("Initializing database...")
    create_tables()
    logger.info("Database initialized successfully")


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


class DatabaseSession:
    """
    Context manager for database sessions.

    Usage:
    ```
    with DatabaseSession() as db:
        result = db.query(Model).all()
    ```
    """

    def __enter__(self) -> Session:
        self.db = SessionLocal()
        return self.db

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.db.rollback()
        self.db.close()
