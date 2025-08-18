"""
Lead Management Models
Erweiterte Models für Lead Scoring, Enrichment und Follow-Up
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
from pydantic import EmailStr
import uuid


class LeadStatus(str, Enum):
    """Lead Status Enum"""
    NEW = "new"
    QUALIFIED = "qualified"
    CONTACTED = "contacted"
    NURTURING = "nurturing"
    CONVERTED = "converted"
    LOST = "lost"


class LeadSource(str, Enum):
    """Lead Source Enum"""
    WEBSITE = "website"
    ADS = "ads"
    COLD = "cold"
    REFERRAL = "referral"
    INBOUND = "inbound"
    SOCIAL = "social"
    EVENT = "event"
    OTHER = "other"


class LeadScore(str, Enum):
    """Lead Score Categories"""
    HOT = "hot"        # 8-10
    WARM = "warm"      # 5-7
    COLD = "cold"      # 1-4


class Lead(SQLModel, table=True):
    """Enhanced Lead Model with Scoring and Enrichment"""
    __tablename__ = "leads"
    
    # Primary Key
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Organization
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    
    # Basic Information
    phone: str = Field(max_length=20, index=True, description="Primary phone number")
    email: Optional[EmailStr] = Field(default=None, index=True)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    company_name: Optional[str] = Field(default=None, max_length=200)
    
    # Lead Scoring (1-10)
    lead_score: int = Field(default=5, ge=1, le=10, description="Lead score from 1-10")
    score_category: LeadScore = Field(default=LeadScore.WARM)
    score_reasons: List[str] = Field(
        default_factory=list, 
        sa_column=Column(JSON),
        description="Reasons for the current score"
    )
    score_updated_at: Optional[datetime] = Field(default=None)
    
    # Lead Enrichment Data
    linkedin_url: Optional[str] = Field(default=None, max_length=500)
    company_size: Optional[str] = Field(default=None, max_length=50)
    industry: Optional[str] = Field(default=None, max_length=100)
    position: Optional[str] = Field(default=None, max_length=200)
    website: Optional[str] = Field(default=None, max_length=500)
    enrichment_data: Dict[str, Any] = Field(
        default_factory=dict,
        sa_column=Column(JSON),
        description="Additional enrichment data from external sources"
    )
    enrichment_updated_at: Optional[datetime] = Field(default=None)
    
    # Lead Status & Tracking
    status: LeadStatus = Field(default=LeadStatus.NEW, index=True)
    source: LeadSource = Field(default=LeadSource.INBOUND, index=True)
    campaign: Optional[str] = Field(default=None, max_length=100, description="Marketing campaign")
    
    # Contact History
    first_contact_date: Optional[datetime] = Field(default=None)
    last_contact_date: Optional[datetime] = Field(default=None)
    next_follow_up: Optional[datetime] = Field(default=None, index=True)
    follow_up_count: int = Field(default=0, description="Number of follow-ups made")
    
    # Conversion Tracking
    converted: bool = Field(default=False)
    converted_date: Optional[datetime] = Field(default=None)
    conversion_value: Optional[float] = Field(default=None, description="Deal value in EUR")
    lost_reason: Optional[str] = Field(default=None, max_length=500)
    
    # Communication Preferences
    preferred_contact_method: str = Field(default="phone", max_length=20)
    preferred_contact_time: Optional[str] = Field(default=None, max_length=50)
    language: str = Field(default="de", max_length=5)
    timezone: str = Field(default="Europe/Berlin", max_length=50)
    
    # Notes & Tags
    notes: Optional[str] = Field(default=None, sa_column=Column(JSON))
    tags: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )
    
    # Relationships
    call_logs: List["CallLog"] = Relationship(back_populates="lead")
    follow_ups: List["FollowUp"] = Relationship(back_populates="lead")
    
    def update_score_category(self):
        """Update score category based on lead score"""
        if self.lead_score >= 8:
            self.score_category = LeadScore.HOT
        elif self.lead_score >= 5:
            self.score_category = LeadScore.WARM
        else:
            self.score_category = LeadScore.COLD
    
    def calculate_days_since_contact(self) -> Optional[int]:
        """Calculate days since last contact"""
        if self.last_contact_date:
            delta = datetime.now(timezone.utc) - self.last_contact_date
            return delta.days
        return None


class FollowUp(SQLModel, table=True):
    """Follow-Up Tasks for Leads"""
    __tablename__ = "follow_ups"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Lead Relationship
    lead_id: int = Field(foreign_key="leads.id", index=True)
    lead: Lead = Relationship(back_populates="follow_ups")
    
    # Follow-Up Details
    scheduled_date: datetime = Field(index=True, description="When to follow up")
    follow_up_number: int = Field(default=1, description="Which follow-up attempt (1st, 2nd, etc)")
    script_type: str = Field(default="follow_up", max_length=50)
    
    # Status
    status: str = Field(default="pending", max_length=20)  # pending/completed/skipped
    completed_date: Optional[datetime] = Field(default=None)
    
    # Results
    outcome: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000)
    call_log_id: Optional[int] = Field(default=None, foreign_key="call_logs.id")
    
    # Priority
    priority: str = Field(default="medium", max_length=20)  # low/medium/high/urgent
    
    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: Optional[datetime] = Field(default=None)


class LeadActivity(SQLModel, table=True):
    """Track all lead activities for timeline view"""
    __tablename__ = "lead_activities"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Lead Relationship
    lead_id: int = Field(foreign_key="leads.id", index=True)
    
    # Activity Details
    activity_type: str = Field(max_length=50, index=True)  # call/email/meeting/note/score_change
    description: str = Field(max_length=500)
    activity_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # User who performed the activity
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Timestamp
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        index=True
    )