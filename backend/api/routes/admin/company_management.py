"""
Company Management API
Admin endpoints for managing multi-tenant companies
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Body
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

from api.models.company import Company, KnowledgeBase, Document, CompanyIntent, Appointment
from api.models.auth import User
from api.services.knowledge_service import KnowledgeService
from api.services.auth_service import get_current_admin_user
from api.core.database import get_session
from sqlmodel import select, func
from pydantic import BaseModel

router = APIRouter(prefix="/admin/companies", tags=["admin", "companies"])

# Pydantic models for requests/responses
class CompanyCreate(BaseModel):
    name: str
    slug: str
    business_type: str = "general"
    subscription_plan: str = "free"
    timezone: str = "UTC"
    voice_personality: str = "friendly"
    voice_language: str = "en-US"
    greeting_message: Optional[str] = None

class CompanyUpdate(BaseModel):
    name: Optional[str] = None
    business_type: Optional[str] = None
    subscription_plan: Optional[str] = None
    business_hours: Optional[Dict[str, str]] = None
    settings: Optional[Dict[str, Any]] = None
    voice_personality: Optional[str] = None
    voice_language: Optional[str] = None
    greeting_message: Optional[str] = None
    system_prompt_template: Optional[str] = None

class IntentCreate(BaseModel):
    intent_name: str
    description: Optional[str] = None
    keywords: List[str] = []
    example_phrases: List[str] = []
    action_type: str
    action_config: Dict[str, Any] = {}
    requires_confirmation: bool = False
    priority: int = 0

@router.post("/", response_model=Company)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a new company/tenant
    """
    async with get_session() as session:
        # Check if slug already exists
        existing = await session.execute(
            select(Company).where(Company.slug == company_data.slug)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(400, "Company slug already exists")
        
        # Create company
        company = Company(**company_data.dict())
        session.add(company)
        await session.commit()
        await session.refresh(company)
        
        # Initialize knowledge base
        knowledge_service = KnowledgeService()
        knowledge_base = await knowledge_service.create_knowledge_base(company)
        
        return company

@router.get("/", response_model=List[Company])
async def list_companies(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all companies
    """
    async with get_session() as session:
        result = await session.execute(
            select(Company)
            .where(Company.is_active == True)
            .offset(skip)
            .limit(limit)
        )
        companies = result.scalars().all()
        return companies

@router.get("/{company_id}", response_model=Company)
async def get_company(
    company_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get company details
    """
    async with get_session() as session:
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(404, "Company not found")
        return company

@router.patch("/{company_id}", response_model=Company)
async def update_company(
    company_id: str,
    update_data: CompanyUpdate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Update company settings
    """
    async with get_session() as session:
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(404, "Company not found")
        
        # Update fields
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(company, field, value)
        
        company.updated_at = datetime.utcnow()
        session.add(company)
        await session.commit()
        await session.refresh(company)
        
        return company

@router.delete("/{company_id}")
async def delete_company(
    company_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Soft delete a company
    """
    async with get_session() as session:
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(404, "Company not found")
        
        company.is_active = False
        company.updated_at = datetime.utcnow()
        session.add(company)
        await session.commit()
        
        return {"message": "Company deactivated"}

# Knowledge Base endpoints
@router.post("/{company_id}/knowledge/upload")
async def upload_document(
    company_id: str,
    file: UploadFile = File(...),
    metadata: Optional[str] = Body(None),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Upload a document to company's knowledge base
    """
    async with get_session() as session:
        # Get company and knowledge base
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(404, "Company not found")
        
        result = await session.execute(
            select(KnowledgeBase).where(KnowledgeBase.company_id == company_id)
        )
        knowledge_base = result.scalar_one_or_none()
        
        if not knowledge_base:
            # Create knowledge base if doesn't exist
            knowledge_service = KnowledgeService()
            knowledge_base = await knowledge_service.create_knowledge_base(company)
        
    # Upload document
    knowledge_service = KnowledgeService()
    document = await knowledge_service.upload_document(
        knowledge_base,
        file,
        metadata=metadata if metadata else {}
    )
    
    return {
        "document_id": document.id,
        "filename": document.filename,
        "status": document.processing_status
    }

@router.get("/{company_id}/knowledge/documents")
async def list_documents(
    company_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all documents in knowledge base
    """
    async with get_session() as session:
        result = await session.execute(
            select(Document)
            .join(KnowledgeBase)
            .where(KnowledgeBase.company_id == company_id)
        )
        documents = result.scalars().all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "chunk_count": doc.chunk_count,
                "uploaded_at": doc.uploaded_at,
                "processing_status": doc.processing_status
            }
            for doc in documents
        ]

@router.delete("/{company_id}/knowledge/documents/{document_id}")
async def delete_document(
    company_id: str,
    document_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a document from knowledge base
    """
    async with get_session() as session:
        # Verify document belongs to company
        result = await session.execute(
            select(Document)
            .join(KnowledgeBase)
            .where(Document.id == document_id)
            .where(KnowledgeBase.company_id == company_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(404, "Document not found")
    
    # Delete document
    knowledge_service = KnowledgeService()
    await knowledge_service.delete_document(document)
    
    return {"message": "Document deleted"}

# Intent Management
@router.post("/{company_id}/intents", response_model=CompanyIntent)
async def create_intent(
    company_id: str,
    intent_data: IntentCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Create a custom intent for company
    """
    async with get_session() as session:
        # Verify company exists
        company = await session.get(Company, company_id)
        if not company:
            raise HTTPException(404, "Company not found")
        
        # Create intent
        intent = CompanyIntent(
            company_id=company_id,
            **intent_data.dict()
        )
        session.add(intent)
        await session.commit()
        await session.refresh(intent)
        
        return intent

@router.get("/{company_id}/intents", response_model=List[CompanyIntent])
async def list_intents(
    company_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    List company's custom intents
    """
    async with get_session() as session:
        result = await session.execute(
            select(CompanyIntent)
            .where(CompanyIntent.company_id == company_id)
            .order_by(CompanyIntent.priority.desc())
        )
        intents = result.scalars().all()
        return intents

# Analytics
@router.get("/{company_id}/analytics/overview")
async def get_analytics_overview(
    company_id: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Get analytics overview for company
    """
    async with get_session() as session:
        # Get appointment stats
        appointment_result = await session.execute(
            select(
                func.count(Appointment.id).label("total_appointments"),
                func.count(Appointment.id).filter(Appointment.status == "confirmed").label("confirmed"),
                func.count(Appointment.id).filter(Appointment.status == "cancelled").label("cancelled")
            )
            .where(Appointment.company_id == company_id)
        )
        appointment_stats = appointment_result.first()
        
        # Get knowledge base stats
        kb_result = await session.execute(
            select(KnowledgeBase)
            .where(KnowledgeBase.company_id == company_id)
        )
        knowledge_base = kb_result.scalar_one_or_none()
        
        return {
            "appointments": {
                "total": appointment_stats.total_appointments if appointment_stats else 0,
                "confirmed": appointment_stats.confirmed if appointment_stats else 0,
                "cancelled": appointment_stats.cancelled if appointment_stats else 0
            },
            "knowledge_base": {
                "document_count": knowledge_base.document_count if knowledge_base else 0,
                "total_chunks": knowledge_base.total_chunks if knowledge_base else 0,
                "last_updated": knowledge_base.last_updated if knowledge_base else None
            }
        }

@router.get("/{company_id}/appointments")
async def list_appointments(
    company_id: str,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_admin_user)
):
    """
    List company's appointments
    """
    async with get_session() as session:
        query = select(Appointment).where(Appointment.company_id == company_id)
        
        if status:
            query = query.where(Appointment.status == status)
        
        query = query.order_by(Appointment.scheduled_datetime.desc())
        query = query.offset(skip).limit(limit)
        
        result = await session.execute(query)
        appointments = result.scalars().all()
        
        return appointments