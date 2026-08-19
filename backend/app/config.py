"""
Application configuration management.
Loads settings from environment variables and provides centralized access.
"""

import os
from pathlib import Path
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )
    
    # Application Settings
    APP_NAME: str = "Financial Advisor API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    
    # CORS Settings
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Database Settings
    DATABASE_URL: str = "sqlite:///./financial_advisor.db"
    DB_ECHO: bool = False  # Set to True to log SQL queries
    
    # Groq API Settings
    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_TEMPERATURE: float = 0.7
    GROQ_MAX_TOKENS: int = 4096
    
    # LLM Settings
    LLM_MAX_RETRIES: int = 3
    LLM_RETRY_DELAY: float = 1.0  # seconds
    LLM_TIMEOUT: int = 30  # seconds
    
    # Security Settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_SECRET_KEY: str = "your-jwt-secret-key-here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440  # 24 hours
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # Logging Settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Financial Planning Defaults
    DEFAULT_INFLATION_RATE: float = 0.03  # 3% annual
    DEFAULT_SAVINGS_RATE: float = 0.05  # 5% annual return
    DEFAULT_EQUITY_RETURN: float = 0.12  # 12% annual return
    DEFAULT_DEBT_RETURN: float = 0.08  # 8% annual return
    
    # Risk Assessment Thresholds
    LOW_RISK_MAX: int = 33
    MEDIUM_RISK_MAX: int = 66
    HIGH_RISK_MIN: int = 67

    @field_validator("DEBUG", mode="before")
    @classmethod
    def normalize_debug_value(cls, value):
        """Accept common build-mode values from global DEBUG variables."""

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"release", "production", "prod"}:
                return False
            if normalized in {"development", "dev", "debug"}:
                return True
        return value

@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    This ensures we load the settings only once during application lifetime.
    """
    return Settings()


# Convenience function to get base directory
def get_base_dir() -> Path:
    """Get the base directory of the backend application."""
    return Path(__file__).resolve().parent.parent


# Convenience function to get data directory
def get_data_dir() -> Path:
    """Get the data directory for storing files."""
    data_dir = get_base_dir() / "data"
    data_dir.mkdir(exist_ok=True)
    return data_dir
