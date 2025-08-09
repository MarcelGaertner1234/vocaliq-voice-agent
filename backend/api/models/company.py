"""
Company Models for Multi-Tenant Support
Handles different businesses using the VocalIQ platform
"""

from sqlmodel import SQLModel, Field, Column, JSON, Relationship
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

class SubscriptionPlan(str, Enum):
    """Available subscription plans"""
    FREE = "free"
    STARTER = "starter" 
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class VoicePersonality(str, Enum):
    """Voice personality types"""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    CASUAL = "casual"
    FORMAL = "formal"

class Company(SQLModel, table=True):
    """
    Company/Tenant model
    Each company has its own voice agent configuration
    """
    __tablename__ = "companies"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    slug: str = Field(unique=True, index=True)  # URL-friendly identifier
    
    # Subscription
    subscription_plan: SubscriptionPlan = Field(default=SubscriptionPlan.FREE)
    subscription_expires: Optional[datetime] = None
    
    # Twilio Configuration
    twilio_phone_number: Optional[str] = None
    twilio_account_sid: Optional[str] = None
    twilio_auth_token_encrypted: Optional[str] = None  # Encrypted!
    
    # Voice Configuration
    voice_personality: VoicePersonality = Field(default=VoicePersonality.FRIENDLY)
    voice_language: str = Field(default="en-US")
    elevenlabs_voice_id: Optional[str] = None
    
    # Business Information
    business_type: str = Field(default="general")  # restaurant, medical, retail, etc.
    business_hours: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    timezone: str = Field(default="UTC")
    
    # Features & Settings
    features: Dict[str, bool] = Field(default_factory=lambda: {
        "reservations": False,
        "appointments": False,
        "knowledge_base": True,
        "call_transfers": False,
        "sms_notifications": False,
        "email_notifications": False
    }, sa_column=Column(JSON))
    
    settings: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # System Prompt Customization
    system_prompt_template: Optional[str] = Field(default=None, sa_column=Column(JSON))
    greeting_message: str = Field(default="Hello! Thank you for calling. How can I help you today?")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    # Relationships
    knowledge_bases: List["KnowledgeBase"] = Relationship(back_populates="company")
    intents: List["CompanyIntent"] = Relationship(back_populates="company")
    appointments: List["Appointment"] = Relationship(back_populates="company")
    call_logs: List["CompanyCallLog"] = Relationship(back_populates="company")

class KnowledgeBase(SQLModel, table=True):
    """
    Knowledge base for each company
    Stores documents and FAQs for RAG
    """
    __tablename__ = "knowledge_bases"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    
    # Weaviate Configuration
    weaviate_namespace: str = Field(unique=True)  # e.g., "Company_abc123"
    
    # Statistics
    document_count: int = Field(default=0)
    total_chunks: int = Field(default=0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    
    # Configuration
    embedding_model: str = Field(default="text-embedding-ada-002")
    chunk_size: int = Field(default=500)
    chunk_overlap: int = Field(default=50)
    
    # Relationships
    company: Company = Relationship(back_populates="knowledge_bases")
    documents: List["Document"] = Relationship(back_populates="knowledge_base")

class Document(SQLModel, table=True):
    """
    Individual documents in knowledge base
    """
    __tablename__ = "documents"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    knowledge_base_id: str = Field(foreign_key="knowledge_bases.id", index=True)
    
    filename: str
    file_type: str  # pdf, docx, txt, html
    file_size: int  # bytes
    
    # Content
    original_text: Optional[str] = None  # Store original for reference
    chunk_count: int = Field(default=0)
    
    # Metadata
    document_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = None
    processing_status: str = Field(default="pending")  # pending, processing, completed, failed
    
    # Relationships
    knowledge_base: KnowledgeBase = Relationship(back_populates="documents")

class CompanyIntent(SQLModel, table=True):
    """
    Custom intents for each company
    Maps user intentions to actions
    """
    __tablename__ = "company_intents"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    
    intent_name: str  # e.g., "make_reservation", "check_hours"
    description: Optional[str] = None
    
    # Recognition
    keywords: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    example_phrases: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Action Configuration
    action_type: str  # reservation, information, transfer, custom
    action_config: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    
    # Settings
    is_enabled: bool = Field(default=True)
    requires_confirmation: bool = Field(default=False)
    priority: int = Field(default=0)  # Higher priority intents are checked first
    
    # Relationships
    company: Company = Relationship(back_populates="intents")

class Appointment(SQLModel, table=True):
    """
    Appointments/Reservations made through voice agent
    """
    __tablename__ = "appointments"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    
    # Customer Information
    customer_phone: str = Field(index=True)
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    
    # Appointment Details
    appointment_type: str  # reservation, appointment, booking
    scheduled_datetime: datetime
    duration_minutes: int = Field(default=60)
    
    # Additional Details (restaurant specific, medical specific, etc.)
    details: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON))
    # e.g., party_size, special_requests, service_type
    
    # Status
    status: str = Field(default="confirmed")  # confirmed, cancelled, completed, no_show
    confirmation_code: str = Field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    
    # Notifications
    reminder_sent: bool = Field(default=False)
    confirmation_sent: bool = Field(default=False)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_via: str = Field(default="voice")  # voice, web, api
    
    # Call Reference
    call_sid: Optional[str] = None  # Twilio Call SID
    
    # Relationships
    company: Company = Relationship(back_populates="appointments")

class CompanyCallLog(SQLModel, table=True):
    """
    Detailed call logs for analytics
    """
    __tablename__ = "company_call_logs"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    company_id: str = Field(foreign_key="companies.id", index=True)
    
    # Call Information
    call_sid: str = Field(unique=True, index=True)
    from_number: str
    to_number: str
    
    # Timing
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    
    # Conversation
    transcript: Optional[str] = Field(default=None, sa_column=Column(JSON))
    intents_detected: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    actions_taken: List[Dict[str, Any]] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Outcome
    call_outcome: Optional[str] = None  # completed, transferred, voicemail, error
    customer_satisfaction: Optional[int] = None  # 1-5 rating
    
    # Analytics
    sentiment_score: Optional[float] = None  # -1 to 1
    keywords_extracted: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    
    # Cost
    twilio_cost: Optional[float] = None
    openai_cost: Optional[float] = None
    elevenlabs_cost: Optional[float] = None
    
    # Relationships
    company: Company = Relationship(back_populates="call_logs")