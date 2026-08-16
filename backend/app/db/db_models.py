"""
SQLAlchemy ORM models for the Finance Planner database.

Current models:
    Customer
    Goal

The Customer and Goal models are based on the synthetic
customer dataset used by the Data Engineer module.
"""

from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


# ============================================================
# Customer Model
# ============================================================

class Customer(Base):
    """
    Stores a customer's financial profile.
    """

    __tablename__ = "customers"

    # --------------------------------------------------------
    # Primary key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Personal information
    # --------------------------------------------------------

    customer_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
    )

    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # --------------------------------------------------------
    # Monthly financial information
    # --------------------------------------------------------

    monthly_income: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    monthly_expenses: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    # --------------------------------------------------------
    # Financial position
    # --------------------------------------------------------

    savings: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_assets: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    total_liabilities: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    # --------------------------------------------------------
    # Risk profile
    # --------------------------------------------------------

    likely_risk_category: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    # --------------------------------------------------------
    # Timestamps
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    # --------------------------------------------------------
    # Relationship with Goal
    # --------------------------------------------------------

    goals: Mapped[list["Goal"]] = relationship(
        "Goal",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


# ============================================================
# Goal Model
# ============================================================

class Goal(Base):
    """
    Stores a customer's financial goal.
    """

    __tablename__ = "goals"

    # --------------------------------------------------------
    # Primary key
    # --------------------------------------------------------

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )

    # --------------------------------------------------------
    # Customer relationship
    # --------------------------------------------------------

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"),
        nullable=False,
        index=True,
    )

    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="goals",
    )

    # --------------------------------------------------------
    # Goal information
    # --------------------------------------------------------

    goal_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    target_amount: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )

    current_goal_savings: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    time_horizon_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )
    