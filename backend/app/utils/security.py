"""
Security utilities for authentication and authorization.
Handles password hashing, JWT token creation/validation, and user authentication.
"""

import os
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.models.auth import TokenData


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# JWT settings from environment variables
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 hours default


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against a hashed password.
    
    Args:
        plain_password: The plain text password to verify
        hashed_password: The hashed password to compare against
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.
    
    Args:
        password: The plain text password to hash
        
    Returns:
        The hashed password
    """
    # Generate salt and hash password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing claims to encode in the token
        expires_delta: Optional expiration time delta (defaults to JWT_EXPIRE_MINUTES)
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=JWT_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT access token.
    
    Args:
        token: The JWT token to decode
        
    Returns:
        TokenData object if valid, None if invalid
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        
        if email is None:
            return None
            
        return TokenData(email=email, user_id=user_id)
        
    except JWTError:
        return None


def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session
        email: User's email address
        password: User's plain text password
        
    Returns:
        User object if authentication successful, False otherwise
    """
    user = crud.get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    Get the current authenticated user from JWT token.
    
    This is a FastAPI dependency that extracts and validates the JWT token,
    then retrieves the user from the database.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found (401 Unauthorized)
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = decode_access_token(token)
    if token_data is None or token_data.email is None:
        raise credentials_exception
    
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user)
):
    """
    Get the current active user.
    
    This is an additional layer that can be used to check if user is active/enabled.
    For now, it just returns the current user, but can be extended to check
    user status if we add an 'is_active' field to the User model.
    
    Args:
        current_user: The authenticated user from get_current_user
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user is inactive (400 Bad Request)
    """
    # Future: Add is_active check here if needed
    # if not current_user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    
    return current_user


def verify_user_owns_customer(user_id: int, customer_id: int, db: Session) -> bool:
    """
    Verify that a user owns a specific customer profile.
    
    Args:
        user_id: ID of the user
        customer_id: ID of the customer profile
        db: Database session
        
    Returns:
        True if user owns the customer profile, False otherwise
    """
    customer = crud.get_customer_profile(db, customer_id)
    if not customer:
        return False
    
    # Check if customer belongs to user
    return customer.user_id == user_id


def require_customer_ownership(user_id: int, customer_id: int, db: Session):
    """
    Require that a user owns a specific customer profile.
    
    Raises HTTPException if user doesn't own the customer profile.
    
    Args:
        user_id: ID of the user
        customer_id: ID of the customer profile
        db: Database session
        
    Raises:
        HTTPException: 403 Forbidden if user doesn't own the profile
        HTTPException: 404 Not Found if customer doesn't exist
    """
    customer = crud.get_customer_profile(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer profile {customer_id} not found"
        )
    
    if customer.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to access this customer profile"
        )
