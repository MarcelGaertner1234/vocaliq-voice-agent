"""
Lead Management API Routes
CRUD Operations und Metriken für Lead Management
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select, and_, or_, func
from pydantic import BaseModel

from api.core.database import get_session
from api.core.auth import get_current_user
from api.models.lead import Lead, LeadStatus, LeadScore, LeadSource
from api.services.lead_scoring_service import LeadScoringService
from api.services.lead_enrichment_service import LeadEnrichmentService
from api.core.subscription import SubscriptionService, Feature

router = APIRouter(
    prefix="/api/leads",
    tags=["lead-management"]
)

# Pydantic Models für Requests/Responses
class LeadCreate(BaseModel):
    first_name: str
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    company_name: Optional[str] = None
    notes: Optional[str] = None
    source: LeadSource = LeadSource.MANUAL

class LeadUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    company_name: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[LeadStatus] = None

class LeadMetrics(BaseModel):
    totalLeads: int
    hotLeads: int
    warmLeads: int
    coldLeads: int
    followUpsDue: int
    conversionRate: float
    averageScore: float
    reactivationCandidates: int


@router.get("", response_model=List[Lead])
async def get_leads(
    session=Depends(get_session),
    current_user=Depends(get_current_user),
    status: Optional[LeadStatus] = None,
    score_category: Optional[LeadScore] = None,
    search: Optional[str] = None,
    limit: int = Query(100, le=500),
    offset: int = 0
):
    """
    Hole alle Leads für die Organisation des Nutzers
    
    Query Parameters:
    - status: Filter nach Lead Status
    - score_category: Filter nach Score Kategorie (hot/warm/cold)
    - search: Suche in Name, Email, Telefon
    - limit: Max Anzahl Ergebnisse
    - offset: Pagination Offset
    """
    # Base query
    query = select(Lead).where(
        Lead.organization_id == current_user.organization_id
    )
    
    # Apply filters
    if status:
        query = query.where(Lead.status == status)
    
    if score_category:
        query = query.where(Lead.score_category == score_category)
    
    if search:
        search_term = f"%{search}%"
        query = query.where(
            or_(
                Lead.first_name.ilike(search_term),
                Lead.last_name.ilike(search_term),
                Lead.phone.ilike(search_term),
                Lead.email.ilike(search_term),
                Lead.company_name.ilike(search_term)
            )
        )
    
    # Order by score (highest first) and limit
    query = query.order_by(Lead.lead_score.desc()).limit(limit).offset(offset)
    
    result = await session.exec(query)
    leads = result.all()
    
    return leads


@router.get("/metrics", response_model=LeadMetrics)
async def get_lead_metrics(
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Hole Lead Metriken für das Dashboard
    """
    org_id = current_user.organization_id
    
    # Total leads
    total_query = select(func.count(Lead.id)).where(
        Lead.organization_id == org_id
    )
    total_result = await session.exec(total_query)
    total_leads = total_result.one()
    
    # Hot leads
    hot_query = select(func.count(Lead.id)).where(
        and_(
            Lead.organization_id == org_id,
            Lead.score_category == LeadScore.HOT
        )
    )
    hot_result = await session.exec(hot_query)
    hot_leads = hot_result.one()
    
    # Warm leads
    warm_query = select(func.count(Lead.id)).where(
        and_(
            Lead.organization_id == org_id,
            Lead.score_category == LeadScore.WARM
        )
    )
    warm_result = await session.exec(warm_query)
    warm_leads = warm_result.one()
    
    # Cold leads
    cold_query = select(func.count(Lead.id)).where(
        and_(
            Lead.organization_id == org_id,
            Lead.score_category == LeadScore.COLD
        )
    )
    cold_result = await session.exec(cold_query)
    cold_leads = cold_result.one()
    
    # Converted leads for conversion rate
    converted_query = select(func.count(Lead.id)).where(
        and_(
            Lead.organization_id == org_id,
            Lead.status == LeadStatus.CONVERTED
        )
    )
    converted_result = await session.exec(converted_query)
    converted_leads = converted_result.one()
    
    # Average score
    avg_query = select(func.avg(Lead.lead_score)).where(
        Lead.organization_id == org_id
    )
    avg_result = await session.exec(avg_query)
    avg_score = avg_result.one() or 0
    
    # Follow-ups due (simplified - would need follow_ups table)
    follow_ups_due = 0  # TODO: Implement when follow_ups table exists
    
    # Reactivation candidates (inactive > 30 days)
    from datetime import timedelta
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    reactivation_query = select(func.count(Lead.id)).where(
        and_(
            Lead.organization_id == org_id,
            Lead.last_contact_date < cutoff_date,
            Lead.status != LeadStatus.CONVERTED,
            Lead.status != LeadStatus.LOST
        )
    )
    reactivation_result = await session.exec(reactivation_query)
    reactivation_candidates = reactivation_result.one()
    
    return LeadMetrics(
        totalLeads=total_leads,
        hotLeads=hot_leads,
        warmLeads=warm_leads,
        coldLeads=cold_leads,
        followUpsDue=follow_ups_due,
        conversionRate=round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 2),
        averageScore=round(avg_score, 1),
        reactivationCandidates=reactivation_candidates
    )


@router.get("/{lead_id}", response_model=Lead)
async def get_lead(
    lead_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Hole Details eines spezifischen Leads
    """
    query = select(Lead).where(
        and_(
            Lead.id == lead_id,
            Lead.organization_id == current_user.organization_id
        )
    )
    result = await session.exec(query)
    lead = result.first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nicht gefunden"
        )
    
    return lead


@router.post("", response_model=Lead)
async def create_lead(
    lead_data: LeadCreate,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Erstelle einen neuen Lead
    """
    # Check if user has lead_scoring feature
    if not SubscriptionService.has_feature(
        current_user.subscription_plan,
        Feature.LEAD_SCORING
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lead Management ist in Ihrem Plan nicht verfügbar"
        )
    
    # Create lead
    lead = Lead(
        organization_id=current_user.organization_id,
        **lead_data.dict(),
        status=LeadStatus.NEW,
        lead_score=5,  # Default score
        score_category=LeadScore.WARM,
        first_contact_date=datetime.now(timezone.utc),
        created_by_user_id=current_user.id
    )
    
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    
    # Trigger enrichment if available
    if SubscriptionService.has_feature(
        current_user.subscription_plan,
        Feature.LEAD_ENRICHMENT
    ):
        # TODO: Trigger async enrichment
        pass
    
    return lead


@router.put("/{lead_id}", response_model=Lead)
async def update_lead(
    lead_id: int,
    lead_update: LeadUpdate,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Aktualisiere einen Lead
    """
    # Get existing lead
    query = select(Lead).where(
        and_(
            Lead.id == lead_id,
            Lead.organization_id == current_user.organization_id
        )
    )
    result = await session.exec(query)
    lead = result.first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nicht gefunden"
        )
    
    # Update fields
    update_data = lead_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(lead, field, value)
    
    lead.last_contact_date = datetime.now(timezone.utc)
    
    session.add(lead)
    await session.commit()
    await session.refresh(lead)
    
    return lead


@router.delete("/{lead_id}")
async def delete_lead(
    lead_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Lösche einen Lead
    """
    # Get existing lead
    query = select(Lead).where(
        and_(
            Lead.id == lead_id,
            Lead.organization_id == current_user.organization_id
        )
    )
    result = await session.exec(query)
    lead = result.first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nicht gefunden"
        )
    
    await session.delete(lead)
    await session.commit()
    
    return {"success": True, "message": "Lead gelöscht"}


@router.post("/{lead_id}/score")
async def update_lead_score(
    lead_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Aktualisiere Lead Score basierend auf Aktivität
    """
    if not SubscriptionService.has_feature(
        current_user.subscription_plan,
        Feature.LEAD_SCORING
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Lead Scoring ist in Ihrem Plan nicht verfügbar"
        )
    
    # Get lead
    query = select(Lead).where(
        and_(
            Lead.id == lead_id,
            Lead.organization_id == current_user.organization_id
        )
    )
    result = await session.exec(query)
    lead = result.first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nicht gefunden"
        )
    
    # Calculate new score
    scoring_service = LeadScoringService()
    
    # Mock call data for scoring
    call_data = {
        'duration': 180,  # 3 minutes
        'transcript': lead.notes or '',
        'appointment_scheduled': False
    }
    
    new_score, reasons = await scoring_service.calculate_score(call_data, lead)
    
    # Update lead
    lead.lead_score = new_score
    lead.score_reasons = reasons
    
    # Update category
    if new_score >= 8:
        lead.score_category = LeadScore.HOT
    elif new_score >= 5:
        lead.score_category = LeadScore.WARM
    else:
        lead.score_category = LeadScore.COLD
    
    session.add(lead)
    await session.commit()
    
    return {
        "success": True,
        "new_score": new_score,
        "category": lead.score_category,
        "reasons": reasons
    }