"""
API routes for customer profile management.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.models import (
    CustomerProfile,
    CustomerProfileCreate,
    CustomerProfileUpdate,
    FinancialSummary,
)
from app.utils.exceptions import CustomerNotFoundException
from app.utils.logger import logger

router = APIRouter(prefix="/profile", tags=["Customer Profile"])


@router.post("/", response_model=CustomerProfile, status_code=status.HTTP_201_CREATED)
def create_customer_profile(
    profile: CustomerProfileCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new customer profile.
    
    Automatically calculates:
    - Net worth (assets - liabilities)
    - Monthly surplus (income - expenses)
    - Debt-to-income ratio
    """
    try:
        logger.info(f"Creating customer profile for: {profile.name}")
        db_profile = crud.create_customer_profile(db, profile)
        logger.info(f"Customer profile created with ID: {db_profile.id}")
        return db_profile
    except Exception as e:
        logger.error(f"Error creating customer profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create customer profile: {str(e)}"
        )


@router.get("/{customer_id}", response_model=CustomerProfile)
def get_customer_profile(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Get a customer profile by ID."""
    db_profile = crud.get_customer_profile(db, customer_id)
    if not db_profile:
        logger.warning(f"Customer profile not found: {customer_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer profile with ID {customer_id} not found"
        )
    return db_profile


@router.get("/", response_model=List[CustomerProfile])
def list_customer_profiles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all customer profiles with pagination."""
    profiles = crud.get_customer_profiles(db, skip=skip, limit=limit)
    return profiles


@router.put("/{customer_id}", response_model=CustomerProfile)
def update_customer_profile(
    customer_id: int,
    profile_update: CustomerProfileUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a customer profile.
    
    Automatically recalculates financial metrics.
    """
    db_profile = crud.update_customer_profile(db, customer_id, profile_update)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer profile with ID {customer_id} not found"
        )
    logger.info(f"Customer profile updated: {customer_id}")
    return db_profile


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_customer_profile(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """Delete a customer profile and all related data (cascade)."""
    success = crud.delete_customer_profile(db, customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer profile with ID {customer_id} not found"
        )
    logger.info(f"Customer profile deleted: {customer_id}")
    return None


@router.get("/{customer_id}/summary", response_model=FinancialSummary)
def get_financial_summary(
    customer_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a comprehensive financial summary for a customer.
    
    Includes:
    - Net worth
    - Monthly surplus
    - Debt-to-income ratio
    - Annual savings capacity
    - Financial health score
    """
    db_profile = crud.get_customer_profile(db, customer_id)
    if not db_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer profile with ID {customer_id} not found"
        )
    
    # Calculate financial health score
    health_score = "Poor"
    if db_profile.monthly_surplus > 0 and db_profile.debt_to_income_ratio < 0.3:
        health_score = "Excellent"
    elif db_profile.monthly_surplus > 0 and db_profile.debt_to_income_ratio < 0.5:
        health_score = "Good"
    elif db_profile.monthly_surplus > 0:
        health_score = "Fair"
    
    summary = FinancialSummary(
        net_worth=db_profile.net_worth,
        monthly_surplus=db_profile.monthly_surplus,
        debt_to_income_ratio=db_profile.debt_to_income_ratio,
        annual_savings_capacity=db_profile.monthly_surplus * 12,
        financial_health_score=health_score,
    )
    
    return summary
