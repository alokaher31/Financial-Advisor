"""
Database connection and session management.
Provides SQLAlchemy engine, session factory, and dependency injection for FastAPI.
"""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from app.config import get_settings
from app.db.db_models import Base
import logging

logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create engine based on database URL
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite-specific configuration
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DB_ECHO,
    )
    
    # Enable foreign key constraints for SQLite
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()
else:
    # PostgreSQL or other database configuration
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,  # Verify connections before using them
        pool_size=5,
        max_overflow=10,
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


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


def init_db():
    """
    Initialize database.
    Creates tables and optionally seeds initial data.
    """
    logger.info("Initializing database...")
    create_tables()
    logger.info("Database initialized successfully")


def get_db_session() -> Session:
    """
    Get a database session for use outside of FastAPI dependency injection.
    
    Usage:
    ```
    db = get_db_session()
    try:
        # Perform database operations
        result = db.query(Model).all()
    finally:
        db.close()
    ```
    
    Returns:
        Session: SQLAlchemy database session
    """
    return SessionLocal()


def check_db_connection() -> bool:
    """
    Check if database connection is working.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("Database connection successful")
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


# Context manager for database sessions
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
