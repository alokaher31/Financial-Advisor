"""
Main FastAPI application entry point.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.db.database import init_db, check_db_connection
from app.api import (
    profile_router,
    risk_router,
    goal_router,
    plan_router,
    chat_router,
)
from app.utils.exceptions import (
    FinancialAdvisorException,
    financial_advisor_exception_handler,
    generic_exception_handler,
    http_exception_handler,
)
from app.utils.logger import logger
from fastapi import HTTPException

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info("Initializing database...")
    
    try:
        init_db()
        if check_db_connection():
            logger.info("Database connection successful")
        else:
            logger.warning("Database connection check failed")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Application shutting down...")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered personal financial planning API",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Register exception handlers
app.add_exception_handler(FinancialAdvisorException, financial_advisor_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Register API routers
app.include_router(profile_router, prefix=settings.API_V1_PREFIX)
app.include_router(risk_router, prefix=settings.API_V1_PREFIX)
app.include_router(goal_router, prefix=settings.API_V1_PREFIX)
app.include_router(plan_router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns application and database status.
    """
    db_status = "healthy" if check_db_connection() else "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": settings.APP_VERSION,
    }


@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "version": settings.APP_VERSION,
        "api_prefix": settings.API_V1_PREFIX,
        "endpoints": {
            "profiles": f"{settings.API_V1_PREFIX}/profile",
            "risk_assessments": f"{settings.API_V1_PREFIX}/risk",
            "goals": f"{settings.API_V1_PREFIX}/goal",
            "plans": f"{settings.API_V1_PREFIX}/plans",
            "chat": f"{settings.API_V1_PREFIX}/chat",
        },
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
