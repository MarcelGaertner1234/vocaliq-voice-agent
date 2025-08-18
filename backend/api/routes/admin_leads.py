"""
Admin Lead Management API Routes
System-weite Lead Verwaltung und Metriken für Admins
"""
from typing import List, Dict
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Query, status
from sqlmodel import select, and_, func
from pydantic import BaseModel

from api.core.database import get_session
from api.core.auth import require_admin
from api.models.lead import Lead, LeadStatus, LeadScore
from api.models.database import Organization
from api.services.lead_reactivation_service import LeadReactivationService

router = APIRouter(
    prefix="/api/admin/leads",
    tags=["admin-leads"],
    dependencies=[Depends(require_admin)]
)

# Response Models
class CompanyMetrics(BaseModel):
    companyId: str
    companyName: str
    subscription: str
    totalLeads: int
    hotLeads: int
    conversionRate: float
    revenueGenerated: float
    lastActivity: datetime
    followUpsDue: int
    reactivationCandidates: int

class SystemMetrics(BaseModel):
    totalCompanies: int
    totalLeads: int
    totalRevenue: float
    averageConversion: float
    activeFollowUps: int
    scheduledReactivations: int
    topPerformers: List[CompanyMetrics]


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics(
    session=Depends(get_session),
    period: str = Query("30d", description="Zeitraum: 7d, 30d, 90d")
):
    """
    Hole system-weite Lead Metriken für Admin Dashboard
    """
    # Parse period
    days = 30
    if period == "7d":
        days = 7
    elif period == "90d":
        days = 90
    
    since_date = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Total companies
    companies_query = select(func.count(Organization.id))
    companies_result = await session.exec(companies_query)
    total_companies = companies_result.one()
    
    # Total leads
    leads_query = select(func.count(Lead.id))
    leads_result = await session.exec(leads_query)
    total_leads = leads_result.one()
    
    # Total revenue (simplified - would need actual revenue tracking)
    revenue_query = select(func.sum(Lead.conversion_value)).where(
        and_(
            Lead.status == LeadStatus.CONVERTED,
            Lead.conversion_date >= since_date
        )
    )
    revenue_result = await session.exec(revenue_query)
    total_revenue = revenue_result.one() or 0.0
    
    # Average conversion rate
    converted_query = select(func.count(Lead.id)).where(
        Lead.status == LeadStatus.CONVERTED
    )
    converted_result = await session.exec(converted_query)
    converted_leads = converted_result.one()
    
    average_conversion = round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 2)
    
    # Active follow-ups (would need FollowUp table)
    active_follow_ups = 0  # TODO: Implement when FollowUp table exists
    
    # Scheduled reactivations
    cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
    reactivation_query = select(func.count(Lead.id)).where(
        and_(
            Lead.last_contact_date < cutoff_date,
            Lead.status != LeadStatus.CONVERTED,
            Lead.status != LeadStatus.LOST
        )
    )
    reactivation_result = await session.exec(reactivation_query)
    scheduled_reactivations = reactivation_result.one()
    
    # Top performers (top 5 companies by conversion rate)
    top_performers = await get_top_performing_companies(session, limit=5)
    
    return SystemMetrics(
        totalCompanies=total_companies,
        totalLeads=total_leads,
        totalRevenue=total_revenue,
        averageConversion=average_conversion,
        activeFollowUps=active_follow_ups,
        scheduledReactivations=scheduled_reactivations,
        topPerformers=top_performers
    )


@router.get("/companies", response_model=List[CompanyMetrics])
async def get_companies_metrics(
    session=Depends(get_session),
    limit: int = Query(50, le=200)
):
    """
    Hole Lead Metriken für alle Firmen
    """
    # Get all organizations
    orgs_query = select(Organization).limit(limit)
    orgs_result = await session.exec(orgs_query)
    organizations = orgs_result.all()
    
    companies_metrics = []
    
    for org in organizations:
        # Get lead metrics for this org
        total_leads_query = select(func.count(Lead.id)).where(
            Lead.organization_id == org.id
        )
        total_leads_result = await session.exec(total_leads_query)
        total_leads = total_leads_result.one()
        
        # Hot leads
        hot_leads_query = select(func.count(Lead.id)).where(
            and_(
                Lead.organization_id == org.id,
                Lead.score_category == LeadScore.HOT
            )
        )
        hot_leads_result = await session.exec(hot_leads_query)
        hot_leads = hot_leads_result.one()
        
        # Conversion rate
        converted_query = select(func.count(Lead.id)).where(
            and_(
                Lead.organization_id == org.id,
                Lead.status == LeadStatus.CONVERTED
            )
        )
        converted_result = await session.exec(converted_query)
        converted_leads = converted_result.one()
        
        conversion_rate = round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 2)
        
        # Revenue
        revenue_query = select(func.sum(Lead.conversion_value)).where(
            and_(
                Lead.organization_id == org.id,
                Lead.status == LeadStatus.CONVERTED
            )
        )
        revenue_result = await session.exec(revenue_query)
        revenue = revenue_result.one() or 0.0
        
        # Last activity
        last_activity_query = select(func.max(Lead.last_contact_date)).where(
            Lead.organization_id == org.id
        )
        last_activity_result = await session.exec(last_activity_query)
        last_activity = last_activity_result.one() or datetime.now(timezone.utc)
        
        # Reactivation candidates
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        reactivation_query = select(func.count(Lead.id)).where(
            and_(
                Lead.organization_id == org.id,
                Lead.last_contact_date < cutoff_date,
                Lead.status != LeadStatus.CONVERTED,
                Lead.status != LeadStatus.LOST
            )
        )
        reactivation_result = await session.exec(reactivation_query)
        reactivation_candidates = reactivation_result.one()
        
        companies_metrics.append(
            CompanyMetrics(
                companyId=str(org.id),
                companyName=org.name,
                subscription=org.subscription_plan or "basic",
                totalLeads=total_leads,
                hotLeads=hot_leads,
                conversionRate=conversion_rate,
                revenueGenerated=revenue,
                lastActivity=last_activity,
                followUpsDue=0,  # TODO: Implement
                reactivationCandidates=reactivation_candidates
            )
        )
    
    # Sort by revenue
    companies_metrics.sort(key=lambda x: x.revenueGenerated, reverse=True)
    
    return companies_metrics


@router.post("/bulk-reactivation")
async def trigger_bulk_reactivation(
    organization_id: Optional[int] = None,
    max_leads: int = Query(50, description="Max Anzahl Leads für Reaktivierung"),
    session=Depends(get_session)
):
    """
    Triggert Massen-Reaktivierung für inaktive Leads
    """
    reactivation_service = LeadReactivationService()
    
    if organization_id:
        # Reaktivierung für spezifische Organisation
        stats = await reactivation_service.bulk_schedule_reactivations(
            organization_id=organization_id,
            max_leads=max_leads
        )
    else:
        # Reaktivierung für alle Organisationen
        orgs_query = select(Organization).where(
            Organization.subscription_plan.in_(["enterprise", "custom"])
        )
        orgs_result = await session.exec(orgs_query)
        organizations = orgs_result.all()
        
        total_stats = {
            '30_days': 0,
            '60_days': 0,
            '90_days': 0,
            '180_days': 0,
            'total': 0
        }
        
        for org in organizations:
            stats = await reactivation_service.bulk_schedule_reactivations(
                organization_id=org.id,
                max_leads=max_leads // len(organizations) if organizations else max_leads
            )
            
            for key in total_stats:
                total_stats[key] += stats.get(key, 0)
        
        stats = total_stats
    
    return {
        "success": True,
        "message": f"Reaktivierung geplant für {stats['total']} Leads",
        "details": stats
    }


async def get_top_performing_companies(
    session,
    limit: int = 5
) -> List[CompanyMetrics]:
    """
    Helper function to get top performing companies
    """
    # Get organizations with most converted leads
    query = (
        select(
            Organization,
            func.count(Lead.id).label("total_leads"),
            func.sum(func.case((Lead.status == LeadStatus.CONVERTED, 1), else_=0)).label("converted_leads"),
            func.sum(func.case((Lead.score_category == LeadScore.HOT, 1), else_=0)).label("hot_leads"),
            func.sum(Lead.conversion_value).label("revenue")
        )
        .join(Lead, Lead.organization_id == Organization.id)
        .group_by(Organization.id)
        .having(func.count(Lead.id) > 0)
        .order_by(func.sum(Lead.conversion_value).desc())
        .limit(limit)
    )
    
    result = await session.exec(query)
    top_companies = result.all()
    
    companies = []
    for org, total_leads, converted_leads, hot_leads, revenue in top_companies:
        conversion_rate = round((converted_leads / total_leads * 100) if total_leads > 0 else 0, 2)
        
        companies.append(
            CompanyMetrics(
                companyId=str(org.id),
                companyName=org.name,
                subscription=org.subscription_plan or "basic",
                totalLeads=total_leads,
                hotLeads=hot_leads or 0,
                conversionRate=conversion_rate,
                revenueGenerated=revenue or 0.0,
                lastActivity=datetime.now(timezone.utc),  # Simplified
                followUpsDue=0,
                reactivationCandidates=0
            )
        )
    
    return companies