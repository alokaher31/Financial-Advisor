import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


# ---------------------------------------------------------
# Load backend/.env
# ---------------------------------------------------------

BACKEND_ROOT = Path(__file__).resolve().parents[2]

load_dotenv(BACKEND_ROOT / ".env")


# ---------------------------------------------------------
# Read database configuration
# ---------------------------------------------------------

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "finance_planner")


if not DB_USER:
    raise RuntimeError(
        "DB_USER is not configured in backend/.env"
    )

if not DB_PASSWORD:
    raise RuntimeError(
        "DB_PASSWORD is not configured in backend/.env"
    )


# ---------------------------------------------------------
# Create PostgreSQL connection URL safely
# ---------------------------------------------------------

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg2",
    username=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=int(DB_PORT),
    database=DB_NAME,
)


# ---------------------------------------------------------
# SQLAlchemy engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ---------------------------------------------------------
# Database session
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
)


# ---------------------------------------------------------
# ORM base
# ---------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------

def get_db():
    """Provide a database session."""

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()