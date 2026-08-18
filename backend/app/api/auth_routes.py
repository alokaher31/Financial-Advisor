"""
Authentication API routes for user registration, login, and profile management.
"""

from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.models.auth import (
    UserCreate, UserLogin, Token, UserOut,
    UserUpdate, PasswordChange
)
from app.utils.security import (
    get_password_hash, verify_password, create_access_token,
    authenticate_user, get_current_user, JWT_EXPIRE_MINUTES
)
from app.utils.logger import logger


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    Creates a new user with hashed password and returns an access token.
    
    Args:
        user_data: User registration data (name, email, password)
        db: Database session
        
    Returns:
        Token object with access_token and expiration info
        
    Raises:
        HTTPException 400: If email is already registered
    """
    # Check if user already exists
    existing_user = crud.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create user
    try:
        db_user = crud.create_user(
            db=db,
            name=user_data.name,
            email=user_data.email,
            hashed_password=hashed_password
        )
        
        logger.info(f"New user registered: {db_user.email} (ID: {db_user.id})")
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": db_user.email, "user_id": db_user.id},
        expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Login with email and password (OAuth2 password flow).
    
    Authenticates user credentials and returns an access token.
    Compatible with OAuth2PasswordBearer for automatic token handling.
    
    Args:
        form_data: OAuth2 form with username (email) and password
        db: Database session
        
    Returns:
        Token object with access_token and expiration info
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        logger.warning(f"Failed login attempt for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.post("/login/json", response_model=Token)
def login_json(
    credentials: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password (JSON body).
    
    Alternative login endpoint that accepts JSON instead of form data.
    Useful for frontend applications that prefer JSON over form encoding.
    
    Args:
        credentials: Login credentials (email, password)
        db: Database session
        
    Returns:
        Token object with access_token and expiration info
        
    Raises:
        HTTPException 401: If credentials are invalid
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate access token
    access_token_expires = timedelta(minutes=JWT_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id},
        expires_delta=access_token_expires
    )
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_MINUTES * 60  # Convert to seconds
    )


@router.get("/me", response_model=UserOut)
async def get_current_user_info(
    current_user = Depends(get_current_user)
):
    """
    Get current authenticated user's information.
    
    Protected endpoint that requires valid JWT token.
    Returns user profile data (excluding password).
    
    Args:
        current_user: The authenticated user (injected by dependency)
        
    Returns:
        User profile information
    """
    return current_user


@router.put("/me", response_model=UserOut)
async def update_current_user_info(
    user_update: UserUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current authenticated user's information.
    
    Allows updating name and/or email.
    Requires valid JWT token.
    
    Args:
        user_update: Updated user data
        current_user: The authenticated user (injected by dependency)
        db: Database session
        
    Returns:
        Updated user profile information
        
    Raises:
        HTTPException 400: If email is already taken by another user
    """
    # Check if email is being changed to one that already exists
    if user_update.email and user_update.email != current_user.email:
        existing_user = crud.get_user_by_email(db, user_update.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Update user
    updated_user = crud.update_user(
        db=db,
        user_id=current_user.id,
        name=user_update.name,
        email=user_update.email
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user information"
        )
    
    logger.info(f"User updated profile: {updated_user.email} (ID: {updated_user.id})")
    
    return updated_user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    password_data: PasswordChange,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change current authenticated user's password.
    
    Requires current password for verification and new password.
    Requires valid JWT token.
    
    Args:
        password_data: Current and new password
        current_user: The authenticated user (injected by dependency)
        db: Database session
        
    Returns:
        204 No Content on success
        
    Raises:
        HTTPException 401: If current password is incorrect
    """
    # Verify current password
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_hashed_password = get_password_hash(password_data.new_password)
    
    # Update password
    updated_user = crud.update_user_password(
        db=db,
        user_id=current_user.id,
        hashed_password=new_hashed_password
    )
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    logger.info(f"User changed password: {current_user.email} (ID: {current_user.id})")
    
    return None


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user_account(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete current authenticated user's account.
    
    Permanently deletes the user account and all associated data.
    This action cannot be undone.
    Requires valid JWT token.
    
    Args:
        current_user: The authenticated user (injected by dependency)
        db: Database session
        
    Returns:
        204 No Content on success
        
    Raises:
        HTTPException 500: If deletion fails
    """
    success = crud.delete_user(db, current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user account"
        )
    
    logger.info(f"User account deleted: {current_user.email} (ID: {current_user.id})")
    
    return None
