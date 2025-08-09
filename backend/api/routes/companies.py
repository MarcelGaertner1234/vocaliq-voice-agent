"""
Companies API Routes - Extended with CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from ..database import get_session
from ..models.company import Company, SubscriptionPlan
from ..auth import get_current_user
from pydantic import BaseModel

router = APIRouter(prefix="/api/companies", tags=["Companies"])

class CompanyCreate(BaseModel):
    """Schema for creating a company"""
    name: str
    slug: str
    subscription_plan: SubscriptionPlan = SubscriptionPlan.FREE
    business_type: str = "general"
    timezone: str = "UTC"

class CompanyUpdate(BaseModel):
    """Schema for updating a company"""
    name: Optional[str] = None
    subscription_plan: Optional[SubscriptionPlan] = None
    business_type: Optional[str] = None
    timezone: Optional[str] = None
    is_active: Optional[bool] = None

class CompanyResponse(BaseModel):
    """Schema for company response"""
    id: str
    name: str
    slug: str
    subscription_plan: SubscriptionPlan
    business_type: str
    timezone: str
    is_active: bool
    created_at: datetime
    user_count: Optional[int] = 0
    call_count: Optional[int] = 0

@router.get("/", response_model=List[CompanyResponse])
async def get_companies(
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get all companies (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    companies = session.exec(select(Company)).all()
    
    # Add user and call counts (mock data for now)
    response = []
    for company in companies:
        company_dict = company.dict()
        # In production, these would be actual counts from related tables
        company_dict["user_count"] = 5  # Mock count
        company_dict["call_count"] = 100  # Mock count
        response.append(CompanyResponse(**company_dict))
    
    return response

@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get a specific company"""
    # Check access rights
    if current_user.get("role") != "admin" and company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    company = session.get(Company, company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    company_dict = company.dict()
    company_dict["user_count"] = 5  # Mock count
    company_dict["call_count"] = 100  # Mock count
    
    return CompanyResponse(**company_dict)

@router.post("/", response_model=CompanyResponse)
async def create_company(
    company_data: CompanyCreate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Create a new company (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Check if slug already exists
    existing = session.exec(
        select(Company).where(Company.slug == company_data.slug)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company slug already exists"
        )
    
    company = Company(**company_data.dict())
    session.add(company)
    session.commit()
    session.refresh(company)
    
    company_dict = company.dict()
    company_dict["user_count"] = 0
    company_dict["call_count"] = 0
    
    return CompanyResponse(**company_dict)

@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: str,
    company_update: CompanyUpdate,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Update a company (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    company = session.get(Company, company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Update fields
    update_data = company_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    
    company.updated_at = datetime.utcnow()
    
    session.add(company)
    session.commit()
    session.refresh(company)
    
    company_dict = company.dict()
    company_dict["user_count"] = 5  # Mock count
    company_dict["call_count"] = 100  # Mock count
    
    return CompanyResponse(**company_dict)

@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Delete a company (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    company = session.get(Company, company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # In production, would need to handle cascading deletes for related data
    session.delete(company)
    session.commit()
    
    return {"message": "Company deleted successfully"}

@router.get("/{company_id}/stats")
async def get_company_stats(
    company_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get company statistics"""
    # Check access rights
    if current_user.get("role") != "admin" and company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    company = session.get(Company, company_id)
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Mock statistics - in production, these would be calculated from actual data
    stats = {
        "total_users": 5,
        "active_users": 4,
        "total_calls": 1234,
        "calls_today": 47,
        "avg_call_duration": 243,  # seconds
        "success_rate": 89,  # percentage
        "knowledge_base_documents": 12,
        "phone_numbers": 3,
        "monthly_cost": 299.99
    }
    
    return stats