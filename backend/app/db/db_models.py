"""
SQLAlchemy ORM models for database tables.
These models define the database schema and relationships.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text,
    ForeignKey, JSON, Boolean, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.database import Base


class CustomerProfileDB(Base):
    """Customer profile database model."""
    __tablename__ = "customer_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(200), nullable=False, index=True)
    age = Column(Integer, nullable=False)
    occupation = Column(String(200), nullable=False)
    monthly_income = Column(Float, nullable=False)
    monthly_expenses = Column(Float, nullable=False)
    total_assets = Column(Float, nullable=False)
    total_liabilities = Column(Float, nullable=False)

    # Calculated fields
    net_worth = Column(Float, nullable=False)
    monthly_surplus = Column(Float, nullable=False)
    debt_to_income_ratio = Column(Float, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    goals = relationship("GoalDB", back_populates="customer", cascade="all, delete-orphan")
    plans = relationship("PlanDB", back_populates="customer", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessmentDB", back_populates="customer", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessageDB", back_populates="customer", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<CustomerProfile(id={self.id}, name='{self.name}')>"


class GoalDB(Base):
    """Financial goal database model."""
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    goal_type = Column(String(50), nullable=False, index=True)
    goal_name = Column(String(200), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_savings = Column(Float, nullable=False, default=0.0)
    time_horizon_years = Column(Integer, nullable=False)
    priority = Column(String(20), nullable=False, default="medium")
    notes = Column(Text, nullable=True)

    # Calculated fields
    required_monthly_saving = Column(Float, nullable=False)
    is_achievable = Column(Boolean, nullable=False, default=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship("CustomerProfileDB", back_populates="goals")

    def __repr__(self):
        return f"<Goal(id={self.id}, name='{self.goal_name}', type='{self.goal_type}')>"


class PlanDB(Base):
    """Financial plan database model."""
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    plan_name = Column(String(200), nullable=False)
    status = Column(String(20), nullable=False, default="draft", index=True)

    # Asset allocation (stored as JSON)
    asset_allocation = Column(JSON, nullable=False)

    # Monthly targets
    monthly_savings_target = Column(Float, nullable=False)

    # Goal allocations (stored as JSON array)
    goal_allocations = Column(JSON, nullable=False)

    # Monthly breakdown (stored as JSON)
    monthly_breakdown = Column(JSON, nullable=False)

    # Assumptions used in plan generation (stored as JSON)
    assumptions = Column(JSON, nullable=False)

    # Additional notes
    notes = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship("CustomerProfileDB", back_populates="plans")

    def __repr__(self):
        return f"<Plan(id={self.id}, name='{self.plan_name}', status='{self.status}')>"


class RiskAssessmentDB(Base):
    """Risk assessment database model."""
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    risk_score = Column(Integer, nullable=False)
    risk_category = Column(String(50), nullable=False, index=True)

    # Questionnaire answers (stored as JSON)
    answers = Column(JSON, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    customer = relationship("CustomerProfileDB", back_populates="risk_assessments")

    def __repr__(self):
        return f"<RiskAssessment(id={self.id}, score={self.risk_score}, category='{self.risk_category}')>"


class ChatMessageDB(Base):
    """Chat message database model."""
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey("customer_profiles.id", ondelete="CASCADE"), nullable=False, index=True)

    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    session_id = Column(String(100), nullable=True, index=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    customer = relationship("CustomerProfileDB", back_populates="chat_messages")

    def __repr__(self):
        return f"<ChatMessage(id={self.id}, role='{self.role}', customer_id={self.customer_id})>"


# Composite indexes for common query patterns
Index('idx_goals_customer_priority', GoalDB.customer_id, GoalDB.priority)
Index('idx_goals_customer_type', GoalDB.customer_id, GoalDB.goal_type)
Index('idx_plans_customer_status', PlanDB.customer_id, PlanDB.status)
Index('idx_chat_customer_session', ChatMessageDB.customer_id, ChatMessageDB.session_id)
Index('idx_chat_session_created', ChatMessageDB.session_id, ChatMessageDB.created_at)
