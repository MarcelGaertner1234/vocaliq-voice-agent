"""
Follow-Up Management API Routes  
Endpoints für Follow-Up Planung und Verwaltung
"""
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import select, and_, or_
from pydantic import BaseModel

from api.core.database import get_session
from api.core.auth import get_current_user
from api.models.lead import Lead, FollowUp
from api.services.follow_up_service import FollowUpService
from api.core.subscription import SubscriptionService, Feature

router = APIRouter(
    prefix="/api/leads",
    tags=["follow-ups"]
)

# Pydantic Models
class FollowUpCreate(BaseModel):
    scheduled_date: datetime
    priority: str = "medium"  # low, medium, high, urgent
    script_type: str = "standard"
    notes: Optional[str] = None

class FollowUpUpdate(BaseModel):
    scheduled_date: Optional[datetime] = None
    priority: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None

class FollowUpResponse(BaseModel):
    id: int
    leadName: str
    scheduledDate: datetime
    followUpNumber: int
    priority: str
    scriptType: str
    status: str = "pending"


@router.get("/follow-ups/upcoming", response_model=List[FollowUpResponse])
async def get_upcoming_follow_ups(
    session=Depends(get_session),
    current_user=Depends(get_current_user),
    days: int = Query(7, description="Tage in die Zukunft"),
    limit: int = Query(50, le=200)
):
    """
    Hole anstehende Follow-Ups für die nächsten X Tage
    """
    # Check feature
    if not SubscriptionService.has_feature(
        current_user.subscription_plan,
        Feature.MANUAL_FOLLOW_UP
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Follow-Up Management ist in Ihrem Plan nicht verfügbar"
        )
    
    # Query upcoming follow-ups
    end_date = datetime.now(timezone.utc) + timedelta(days=days)
    
    query = (
        select(FollowUp, Lead)
        .join(Lead)
        .where(
            and_(
                Lead.organization_id == current_user.organization_id,
                FollowUp.status == "pending",
                FollowUp.scheduled_date <= end_date
            )
        )
        .order_by(FollowUp.scheduled_date)
        .limit(limit)
    )
    
    result = await session.exec(query)
    follow_ups_with_leads = result.all()
    
    # Format response
    response = []
    for follow_up, lead in follow_ups_with_leads:
        response.append(
            FollowUpResponse(
                id=follow_up.id,
                leadName=f"{lead.first_name} {lead.last_name or ''}".strip(),
                scheduledDate=follow_up.scheduled_date,
                followUpNumber=follow_up.follow_up_number,
                priority=follow_up.priority,
                scriptType=follow_up.script_type,
                status=follow_up.status
            )
        )
    
    return response


@router.post("/{lead_id}/follow-ups", response_model=FollowUp)
async def schedule_follow_up(
    lead_id: int,
    follow_up_data: FollowUpCreate,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Plane ein neues Follow-Up für einen Lead
    """
    # Check feature
    if not SubscriptionService.has_feature(
        current_user.subscription_plan,
        Feature.MANUAL_FOLLOW_UP
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Follow-Up Management ist in Ihrem Plan nicht verfügbar"
        )
    
    # Check lead exists and belongs to org
    lead_query = select(Lead).where(
        and_(
            Lead.id == lead_id,
            Lead.organization_id == current_user.organization_id
        )
    )
    lead_result = await session.exec(lead_query)
    lead = lead_result.first()
    
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead nicht gefunden"
        )
    
    # Count existing follow-ups to determine number
    count_query = select(FollowUp).where(FollowUp.lead_id == lead_id)
    count_result = await session.exec(count_query)
    follow_up_count = len(count_result.all())
    
    # Create follow-up
    follow_up = FollowUp(
        lead_id=lead_id,
        scheduled_date=follow_up_data.scheduled_date,
        follow_up_number=follow_up_count + 1,
        priority=follow_up_data.priority,
        script_type=follow_up_data.script_type,
        notes=follow_up_data.notes,
        status="pending"
    )
    
    session.add(follow_up)
    await session.commit()
    await session.refresh(follow_up)
    
    return follow_up


@router.put("/follow-ups/{follow_up_id}", response_model=FollowUp)
async def update_follow_up(
    follow_up_id: int,
    update_data: FollowUpUpdate,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Aktualisiere ein Follow-Up
    """
    # Get follow-up with lead
    query = (
        select(FollowUp, Lead)
        .join(Lead)
        .where(
            and_(
                FollowUp.id == follow_up_id,
                Lead.organization_id == current_user.organization_id
            )
        )
    )
    result = await session.exec(query)
    follow_up_with_lead = result.first()
    
    if not follow_up_with_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-Up nicht gefunden"
        )
    
    follow_up, _ = follow_up_with_lead
    
    # Update fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(follow_up, field, value)
    
    session.add(follow_up)
    await session.commit()
    await session.refresh(follow_up)
    
    return follow_up


@router.post("/follow-ups/{follow_up_id}/complete")
async def complete_follow_up(
    follow_up_id: int,
    outcome: str = Query(..., description="contacted, no_answer, converted, lost"),
    notes: Optional[str] = None,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Markiere ein Follow-Up als abgeschlossen
    """
    # Get follow-up with lead
    query = (
        select(FollowUp, Lead)
        .join(Lead)
        .where(
            and_(
                FollowUp.id == follow_up_id,
                Lead.organization_id == current_user.organization_id
            )
        )
    )
    result = await session.exec(query)
    follow_up_with_lead = result.first()
    
    if not follow_up_with_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow-Up nicht gefunden"
        )
    
    follow_up, lead = follow_up_with_lead
    
    # Update follow-up
    follow_up.status = "completed"
    follow_up.completed_date = datetime.now(timezone.utc)
    follow_up.outcome = outcome
    if notes:
        follow_up.notes = (follow_up.notes or "") + f"\n{notes}"
    
    # Update lead last contact
    lead.last_contact_date = datetime.now(timezone.utc)
    
    # If converted, update lead status
    if outcome == "converted":
        lead.status = "converted"
        lead.conversion_date = datetime.now(timezone.utc)
    elif outcome == "lost":
        lead.status = "lost"
        lead.lost_reason = notes or "Follow-Up nicht erfolgreich"
    
    session.add(follow_up)
    session.add(lead)
    await session.commit()
    
    # Schedule next follow-up if AUTO_FOLLOW_UP is enabled
    if (
        outcome == "contacted" and 
        SubscriptionService.has_feature(
            current_user.subscription_plan,
            Feature.AUTO_FOLLOW_UP
        )
    ):
        follow_up_service = FollowUpService()
        await follow_up_service.schedule_next_follow_up(
            lead_id=lead.id,
            current_follow_up_number=follow_up.follow_up_number
        )
    
    return {
        "success": True,
        "message": f"Follow-Up abgeschlossen: {outcome}",
        "lead_status": lead.status
    }


@router.delete("/follow-ups/{follow_up_id}")
async def cancel_follow_up(
    follow_up_id: int,
    session=Depends(get_session),
    current_user=Depends(get_current_user)
):
    """
    Storniere ein Follow-Up
    """
    # Get follow-up with lead
    query = (
        select(FollowUp, Lead)
        .join(Lead)
        .where(
            and_(
                FollowUp.id == follow_up_id,
                Lead.organization_id == current_user.organization_id,
                FollowUp.status == "pending"
            )
        )
    )
    result = await session.exec(query)
    follow_up_with_lead = result.first()
    
    if not follow_up_with_lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pending Follow-Up nicht gefunden"
        )
    
    follow_up, _ = follow_up_with_lead
    
    # Update status to cancelled
    follow_up.status = "cancelled"
    follow_up.completed_date = datetime.now(timezone.utc)
    follow_up.outcome = "cancelled"
    
    session.add(follow_up)
    await session.commit()
    
    return {"success": True, "message": "Follow-Up storniert"}