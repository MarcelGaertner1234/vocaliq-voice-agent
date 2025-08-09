"""
Phone Numbers API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from ..database import get_session
from ..models.phone_number import (
    PhoneNumber, 
    PhoneNumberCreate, 
    PhoneNumberUpdate, 
    PhoneNumberResponse
)
from ..models.company import Company
from ..auth import get_current_user

router = APIRouter(prefix="/api/phone-numbers", tags=["Phone Numbers"])

@router.get("/", response_model=List[PhoneNumberResponse])
async def get_phone_numbers(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all phone numbers"""
    # Check if user is admin
    if current_user.get("role") != "admin":
        # Filter by company for non-admin users
        statement = select(PhoneNumber).where(
            PhoneNumber.company_id == current_user.get("company_id")
        )
    else:
        statement = select(PhoneNumber)
    
    phone_numbers = session.exec(statement).all()
    
    # Add company names to response
    response = []
    for phone in phone_numbers:
        phone_dict = phone.dict()
        if phone.company_id:
            company = session.get(Company, phone.company_id)
            phone_dict["company_name"] = company.name if company else None
        response.append(PhoneNumberResponse(**phone_dict))
    
    return response

@router.get("/{phone_id}", response_model=PhoneNumberResponse)
async def get_phone_number(
    phone_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific phone number"""
    phone_number = session.get(PhoneNumber, phone_id)
    
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    # Check access rights
    if current_user.get("role") != "admin" and phone_number.company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    phone_dict = phone_number.dict()
    if phone_number.company_id:
        company = session.get(Company, phone_number.company_id)
        phone_dict["company_name"] = company.name if company else None
    
    return PhoneNumberResponse(**phone_dict)

@router.post("/", response_model=PhoneNumberResponse)
async def create_phone_number(
    phone_number: PhoneNumberCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new phone number (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Check if number already exists
    existing = session.exec(
        select(PhoneNumber).where(PhoneNumber.number == phone_number.number)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone number already exists"
        )
    
    db_phone_number = PhoneNumber(**phone_number.dict())
    session.add(db_phone_number)
    session.commit()
    session.refresh(db_phone_number)
    
    phone_dict = db_phone_number.dict()
    if db_phone_number.company_id:
        company = session.get(Company, db_phone_number.company_id)
        phone_dict["company_name"] = company.name if company else None
    
    return PhoneNumberResponse(**phone_dict)

@router.put("/{phone_id}", response_model=PhoneNumberResponse)
async def update_phone_number(
    phone_id: str,
    phone_update: PhoneNumberUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a phone number (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    phone_number = session.get(PhoneNumber, phone_id)
    
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    # Update fields
    update_data = phone_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(phone_number, field, value)
    
    phone_number.updated_at = datetime.utcnow()
    
    session.add(phone_number)
    session.commit()
    session.refresh(phone_number)
    
    phone_dict = phone_number.dict()
    if phone_number.company_id:
        company = session.get(Company, phone_number.company_id)
        phone_dict["company_name"] = company.name if company else None
    
    return PhoneNumberResponse(**phone_dict)

@router.delete("/{phone_id}")
async def delete_phone_number(
    phone_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete a phone number (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    phone_number = session.get(PhoneNumber, phone_id)
    
    if not phone_number:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Phone number not found"
        )
    
    session.delete(phone_number)
    session.commit()
    
    return {"message": "Phone number deleted successfully"}

@router.get("/company/{company_id}", response_model=List[PhoneNumberResponse])
async def get_company_phone_numbers(
    company_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all phone numbers for a specific company"""
    # Check access rights
    if current_user.get("role") != "admin" and company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    statement = select(PhoneNumber).where(PhoneNumber.company_id == company_id)
    phone_numbers = session.exec(statement).all()
    
    company = session.get(Company, company_id)
    company_name = company.name if company else None
    
    response = []
    for phone in phone_numbers:
        phone_dict = phone.dict()
        phone_dict["company_name"] = company_name
        response.append(PhoneNumberResponse(**phone_dict))
    
    return response