"""
Custom exceptions and error handlers for the application.
"""

from typing import Any, Dict
from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from app.utils.logger import logger


class FinancialAdvisorException(Exception):
    """Base exception for all application errors."""
    
    def __init__(self, message: str, details: Dict[str, Any] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class CustomerNotFoundException(FinancialAdvisorException):
    """Raised when a customer is not found in the database."""
    pass


class GoalNotFoundException(FinancialAdvisorException):
    """Raised when a goal is not found in the database."""
    pass


class PlanNotFoundException(FinancialAdvisorException):
    """Raised when a plan is not found in the database."""
    pass


class RiskAssessmentNotFoundException(FinancialAdvisorException):
    """Raised when a risk assessment is not found in the database."""
    pass


class InvalidFinancialDataException(FinancialAdvisorException):
    """Raised when financial data validation fails."""
    pass


class PlanGenerationException(FinancialAdvisorException):
    """Raised when plan generation fails."""
    pass


class LLMException(FinancialAdvisorException):
    """Raised when LLM API call fails."""
    pass


class DatabaseException(FinancialAdvisorException):
    """Raised when database operation fails."""
    pass


# Exception handlers for FastAPI

async def financial_advisor_exception_handler(
    request: Request, 
    exc: FinancialAdvisorException
) -> JSONResponse:
    """Handle custom application exceptions."""
    logger.error(f"Application error: {exc.message}", extra={"details": exc.details})
    
    # Map exception types to HTTP status codes
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    if isinstance(exc, (CustomerNotFoundException, GoalNotFoundException, 
                       PlanNotFoundException, RiskAssessmentNotFoundException)):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, InvalidFinancialDataException):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    elif isinstance(exc, PlanGenerationException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    elif isinstance(exc, LLMException):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    elif isinstance(exc, DatabaseException):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.exception("Unexpected error occurred", exc_info=exc)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "An unexpected error occurred",
            "details": {"message": str(exc)},
            "type": "InternalServerError"
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "type": "HTTPException"
        }
    )
