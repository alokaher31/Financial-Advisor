"""
Pydantic models for API request/response validation.
These models are used for data validation and serialization in the API layer.
"""

from .customer_profile import (
    CustomerProfile,
    CustomerProfileCreate,
    CustomerProfileUpdate,
    CustomerProfileBase,
    FinancialSummary,
)

from .goal import (
    Goal,
    GoalCreate,
    GoalUpdate,
    GoalBase,
    GoalType,
    GoalPriority,
    GoalCalculation,
)

from .plan import (
    Plan,
    PlanCreate,
    PlanUpdate,
    PlanBase,
    PlanStatus,
    PlanCreateRequest,
    AssetAllocation,
    GoalAllocation,
    MonthlyBreakdown,
    PlanComparison,
    WhatIfScenario,
    PlanExplanation,
)

from .risk_assessment import (
    RiskAssessment,
    RiskAssessmentCreate,
    RiskAssessmentBase,
    RiskAnswers,
    RiskProfile,
    RiskQuestion,
    RiskQuestionnaire,
)

from .chat import (
    ChatMessage,
    ChatMessageCreate,
    ChatMessageBase,
    ChatRequest,
    ChatResponse,
    ChatSession,
    ChatHistoryRequest,
    ConversationSummary,
    MessageRole,
)

__all__ = [
    # Customer Profile
    "CustomerProfile",
    "CustomerProfileCreate",
    "CustomerProfileUpdate",
    "CustomerProfileBase",
    "FinancialSummary",
    # Goals
    "Goal",
    "GoalCreate",
    "GoalUpdate",
    "GoalBase",
    "GoalType",
    "GoalPriority",
    "GoalCalculation",
    # Plans
    "Plan",
    "PlanCreate",
    "PlanUpdate",
    "PlanBase",
    "PlanStatus",
    "PlanCreateRequest",
    "AssetAllocation",
    "GoalAllocation",
    "MonthlyBreakdown",
    "PlanComparison",
    "WhatIfScenario",
    "PlanExplanation",
    # Risk Assessment
    "RiskAssessment",
    "RiskAssessmentCreate",
    "RiskAssessmentBase",
    "RiskAnswers",
    "RiskProfile",
    "RiskQuestion",
    "RiskQuestionnaire",
    # Chat
    "ChatMessage",
    "ChatMessageCreate",
    "ChatMessageBase",
    "ChatRequest",
    "ChatResponse",
    "ChatSession",
    "ChatHistoryRequest",
    "ConversationSummary",
    "MessageRole",
]
