from sqlalchemy import text

from app.db.database import engine


def test_database_connection():
    """Verify that the backend can connect to PostgreSQL."""

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))

        assert result.scalar() == 1