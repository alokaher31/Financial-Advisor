"""
API routes package.
Contains all FastAPI router modules.
"""

from .auth_routes import router as auth_router
from .profile_routes import router as profile_router
from .risk_routes import router as risk_router
from .goal_routes import router as goal_router
from .plan_routes import router as plan_router
from .chat_routes import router as chat_router

__all__ = [
    "auth_router",
    "profile_router",
    "risk_router",
    "goal_router",
    "plan_router",
    "chat_router",
]
