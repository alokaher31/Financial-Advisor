"""
Utility modules for logging, error handling, and common functions.
"""

from .logger import logger, setup_logger
from .exceptions import (
    FinancialAdvisorException,
    CustomerNotFoundException,
    GoalNotFoundException,
    PlanNotFoundException,
    RiskAssessmentNotFoundException,
    InvalidFinancialDataException,
    PlanGenerationException,
    LLMException,
    DatabaseException,
    financial_advisor_exception_handler,
    generic_exception_handler,
    http_exception_handler,
)

__all__ = [
    # Logger
    "logger",
    "setup_logger",
    # Exceptions
    "FinancialAdvisorException",
    "CustomerNotFoundException",
    "GoalNotFoundException",
    "PlanNotFoundException",
    "RiskAssessmentNotFoundException",
    "InvalidFinancialDataException",
    "PlanGenerationException",
    "LLMException",
    "DatabaseException",
    # Exception handlers
    "financial_advisor_exception_handler",
    "generic_exception_handler",
    "http_exception_handler",
]
