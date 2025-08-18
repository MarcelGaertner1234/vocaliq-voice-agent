"""
VocalIQ Database Models
SQLModel-basierte Entities für persistente Datenhaltung
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
# EmailStr removed - using str for SQLModel compatibility
import uuid


# Enums für verschiedene Status-Felder
class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    USER = "user"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CallStatus(str, Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class ConversationRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# Base Model mit gemeinsamen Feldern
class TimestampMixin(SQLModel):
    """Mixin für Timestamp-Felder"""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp"
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        description="Last update timestamp"
    )


# Organization Entity
class Organization(TimestampMixin, table=True):
    """Organization/Unternehmen Entity"""
    __tablename__ = "organizations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    name: str = Field(max_length=200, description="Organization name")
    slug: str = Field(max_length=100, unique=True, index=True, description="URL-friendly identifier")
    domain: Optional[str] = Field(default=None, max_length=100, description="Primary domain")
    
    # Contact information
    email: Optional[str] = Field(default=None, description="Primary contact email")
    phone: Optional[str] = Field(default=None, max_length=20, description="Primary phone number")
    website: Optional[str] = Field(default=None, max_length=200, description="Website URL")
    
    # Address
    address_line1: Optional[str] = Field(default=None, max_length=200)
    address_line2: Optional[str] = Field(default=None, max_length=200)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=20)
    country: str = Field(default="DE", max_length=2, description="ISO country code")
    
    # Settings
    timezone: str = Field(default="Europe/Berlin", max_length=50)
    language: str = Field(default="de", max_length=5, description="Primary language")
    
    # Features
    features: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Organization features and settings")
    
    # Subscription & Billing
    subscription_plan: str = Field(default="free", max_length=50)
    subscription_status: str = Field(default="active", max_length=20)
    billing_email: Optional[str] = Field(default=None)
    
    # Status
    is_active: bool = Field(default=True)
    
    # Relationships
    users: List["User"] = Relationship(back_populates="organization")
    phone_numbers: List["PhoneNumber"] = Relationship(back_populates="organization")
    call_logs: List["CallLog"] = Relationship(back_populates="organization")


# User Entity
class User(TimestampMixin, table=True):
    """User Entity"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Organization relationship
    organization_id: Optional[int] = Field(default=None, foreign_key="organizations.id")
    organization: Optional[Organization] = Relationship(back_populates="users")
    
    # Authentication
    email: str = Field(unique=True, index=True, description="User email (login)")
    username: Optional[str] = Field(default=None, max_length=50, unique=True, index=True)
    password_hash: str = Field(description="Bcrypt password hash")
    
    # Profile
    first_name: str = Field(max_length=100, description="First name")
    last_name: str = Field(max_length=100, description="Last name") 
    display_name: Optional[str] = Field(default=None, max_length=200, description="Display name")
    avatar_url: Optional[str] = Field(default=None, max_length=500)
    
    # Contact
    phone: Optional[str] = Field(default=None, max_length=20, description="Personal phone number")
    mobile: Optional[str] = Field(default=None, max_length=20, description="Mobile phone number")
    
    # Role & Permissions
    role: UserRole = Field(default=UserRole.USER, description="User role")
    permissions: List[str] = Field(default_factory=list, sa_column=Column(JSON), description="Specific permissions")
    
    # Status
    status: UserStatus = Field(default=UserStatus.ACTIVE)
    is_verified: bool = Field(default=False, description="Email verified")
    email_verified_at: Optional[datetime] = Field(default=None)
    
    # Settings
    language: str = Field(default="de", max_length=5)
    timezone: str = Field(default="Europe/Berlin", max_length=50)
    preferences: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="User preferences")
    
    # Activity tracking
    last_login_at: Optional[datetime] = Field(default=None)
    last_active_at: Optional[datetime] = Field(default=None)
    login_count: int = Field(default=0)
    
    # Relationships
    call_logs: List["CallLog"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")


# Phone Number Entity
class PhoneNumber(TimestampMixin, table=True):
    """Phone Number Entity für Twilio Integration"""
    __tablename__ = "phone_numbers"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Organization
    organization_id: int = Field(foreign_key="organizations.id")
    organization: Organization = Relationship(back_populates="phone_numbers")
    
    # Phone Number Details
    number: str = Field(unique=True, index=True, description="E.164 format phone number")
    friendly_name: Optional[str] = Field(default=None, max_length=100)
    country_code: str = Field(max_length=3, description="Country code (e.g., +49)")
    
    # Twilio Integration
    twilio_sid: str = Field(unique=True, index=True, description="Twilio Phone Number SID")
    twilio_account_sid: str = Field(description="Twilio Account SID")
    
    # Capabilities
    voice_enabled: bool = Field(default=True)
    sms_enabled: bool = Field(default=True)
    mms_enabled: bool = Field(default=False)
    fax_enabled: bool = Field(default=False)
    
    # Configuration
    voice_url: Optional[str] = Field(default=None, max_length=500, description="Voice webhook URL")
    voice_method: str = Field(default="POST", max_length=10)
    status_callback_url: Optional[str] = Field(default=None, max_length=500)
    
    # Pricing
    monthly_cost: Optional[float] = Field(default=None, description="Monthly cost in EUR")
    per_minute_cost: Optional[float] = Field(default=None, description="Per minute cost in EUR")
    
    # Status
    is_active: bool = Field(default=True)
    
    # Relationships
    call_logs: List["CallLog"] = Relationship(back_populates="phone_number")


# Call Log Entity
class CallLog(TimestampMixin, table=True):
    """Call Log Entity für alle Anruf-Daten"""
    __tablename__ = "call_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Relationships
    organization_id: int = Field(foreign_key="organizations.id")
    organization: Organization = Relationship(back_populates="call_logs")
    
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="call_logs")
    
    phone_number_id: Optional[int] = Field(default=None, foreign_key="phone_numbers.id")
    phone_number: Optional[PhoneNumber] = Relationship(back_populates="call_logs")
    
    # Twilio Data
    twilio_call_sid: str = Field(unique=True, index=True, description="Twilio Call SID")
    twilio_parent_call_sid: Optional[str] = Field(default=None, description="Parent call SID for forwarded calls")
    
    # Call Details
    direction: CallDirection = Field(description="Call direction")
    status: CallStatus = Field(description="Call status")
    
    from_number: str = Field(max_length=20, description="Caller number in E.164 format")
    to_number: str = Field(max_length=20, description="Called number in E.164 format")
    
    # Timing
    start_time: Optional[datetime] = Field(default=None, description="Call start time")
    answer_time: Optional[datetime] = Field(default=None, description="Call answer time")
    end_time: Optional[datetime] = Field(default=None, description="Call end time")
    duration_seconds: Optional[int] = Field(default=None, description="Total call duration")
    billable_seconds: Optional[int] = Field(default=None, description="Billable duration")
    
    # Audio & Recording
    recording_url: Optional[str] = Field(default=None, max_length=500, description="Call recording URL")
    recording_sid: Optional[str] = Field(default=None, description="Twilio Recording SID")
    recording_duration: Optional[int] = Field(default=None, description="Recording duration in seconds")
    
    # AI Processing
    transcription: Optional[str] = Field(default=None, description="Call transcription")
    transcription_confidence: Optional[float] = Field(default=None, description="Transcription confidence score")
    ai_summary: Optional[str] = Field(default=None, description="AI-generated call summary")
    sentiment_score: Optional[float] = Field(default=None, description="Call sentiment analysis score")
    
    # Business Data
    caller_name: Optional[str] = Field(default=None, max_length=200, description="Identified caller name")
    call_purpose: Optional[str] = Field(default=None, max_length=100, description="Call purpose/category")
    lead_status: Optional[str] = Field(default=None, max_length=50, description="Lead qualification status")
    follow_up_required: bool = Field(default=False)
    follow_up_notes: Optional[str] = Field(default=None, description="Follow-up notes")
    
    # Cost & Billing
    cost: Optional[float] = Field(default=None, description="Call cost in EUR")
    cost_currency: str = Field(default="EUR", max_length=3)
    
    # Technical Details
    quality_issues: Optional[Dict[str, Any]] = Field(default=None, sa_column=Column(JSON), description="Audio quality issues")
    forwarded_from: Optional[str] = Field(default=None, max_length=20, description="Original number if forwarded")
    user_agent: Optional[str] = Field(default=None, max_length=200, description="SIP User-Agent")
    
    # Relationships
    conversations: List["Conversation"] = Relationship(back_populates="call_log")


# Conversation Entity (für AI-Chat-Verlauf)
class Conversation(TimestampMixin, table=True):
    """Conversation Entity für AI-Chat-Verlauf"""
    __tablename__ = "conversations"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Relationships
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    user: Optional[User] = Relationship(back_populates="conversations")
    
    call_log_id: Optional[int] = Field(default=None, foreign_key="call_logs.id")
    call_log: Optional[CallLog] = Relationship(back_populates="conversations")
    
    # Session Info
    session_id: str = Field(index=True, description="Session identifier")
    conversation_type: str = Field(default="voice", max_length=20, description="Type: voice, chat, email")
    
    # AI Model Info
    model_name: str = Field(max_length=100, description="AI model used")
    system_prompt: Optional[str] = Field(default=None, description="System prompt used")
    prompt_template: Optional[str] = Field(default=None, max_length=100, description="Prompt template name")
    
    # Message Content
    role: ConversationRole = Field(description="Message role")
    content: str = Field(description="Message content")
    
    # Metadata
    tokens_used: Optional[int] = Field(default=None, description="Tokens consumed")
    response_time_ms: Optional[int] = Field(default=None, description="Response time in milliseconds")
    confidence_score: Optional[float] = Field(default=None, description="AI confidence score")
    
    # Audio specific (für Voice-Chat)
    audio_url: Optional[str] = Field(default=None, max_length=500, description="Audio file URL")
    audio_duration: Optional[float] = Field(default=None, description="Audio duration in seconds")
    audio_format: Optional[str] = Field(default=None, max_length=10, description="Audio format")
    
    # Processing flags
    processed: bool = Field(default=True, description="Message processing completed")
    error_message: Optional[str] = Field(default=None, description="Processing error if any")
    
    # Sequence
    sequence_number: int = Field(description="Message sequence in conversation")


# Analytics/Metrics Entity
class CallAnalytics(TimestampMixin, table=True):
    """Call Analytics Entity für Reporting"""
    __tablename__ = "call_analytics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Time dimensions
    date: datetime = Field(index=True, description="Analytics date")
    hour: int = Field(description="Hour of day (0-23)")
    day_of_week: int = Field(description="Day of week (0=Monday)")
    week: int = Field(description="Week number")
    month: int = Field(description="Month number")
    year: int = Field(description="Year")
    
    # Organization
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    
    # Metrics
    total_calls: int = Field(default=0, description="Total calls")
    answered_calls: int = Field(default=0, description="Answered calls")
    missed_calls: int = Field(default=0, description="Missed calls")
    failed_calls: int = Field(default=0, description="Failed calls")
    
    total_duration: int = Field(default=0, description="Total call duration in seconds")
    avg_duration: float = Field(default=0.0, description="Average call duration")
    
    inbound_calls: int = Field(default=0, description="Inbound calls")
    outbound_calls: int = Field(default=0, description="Outbound calls")
    
    # AI Metrics
    ai_handled_calls: int = Field(default=0, description="Calls handled by AI")
    human_transferred_calls: int = Field(default=0, description="Calls transferred to humans")
    ai_satisfaction_score: Optional[float] = Field(default=None, description="AI satisfaction rating")
    
    # Business Metrics
    leads_generated: int = Field(default=0, description="Leads generated")
    appointments_booked: int = Field(default=0, description="Appointments booked")
    sales_qualified_leads: int = Field(default=0, description="Sales qualified leads")
    
    # Cost Metrics
    total_cost: float = Field(default=0.0, description="Total cost in EUR")
    avg_cost_per_call: float = Field(default=0.0, description="Average cost per call")
    
    # Quality Metrics
    transcription_accuracy: Optional[float] = Field(default=None, description="Average transcription accuracy")
    voice_quality_score: Optional[float] = Field(default=None, description="Average voice quality")


# API Keys & Integration Entity
class APIKey(TimestampMixin, table=True):
    """API Keys Entity für externe Service-Integrationen"""
    __tablename__ = "api_keys"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: str = Field(default_factory=lambda: str(uuid.uuid4()), unique=True, index=True)
    
    # Organization
    organization_id: int = Field(foreign_key="organizations.id", index=True)
    
    # Key Details
    service_name: str = Field(max_length=50, description="Service name (twilio, openai, elevenlabs)")
    key_name: str = Field(max_length=100, description="Key identifier")
    encrypted_key: str = Field(description="Encrypted API key")
    
    # Configuration
    environment: str = Field(default="production", max_length=20, description="Environment (dev/staging/prod)")
    is_active: bool = Field(default=True)
    expires_at: Optional[datetime] = Field(default=None, description="Key expiration")
    
    # Usage tracking
    last_used_at: Optional[datetime] = Field(default=None)
    usage_count: int = Field(default=0, description="Number of times used")
    
    # Metadata
    key_metadata: Dict[str, Any] = Field(default_factory=dict, sa_column=Column(JSON), description="Additional key metadata")


# System Configuration Entity
class SystemConfig(TimestampMixin, table=True):
    """System Configuration Entity"""
    __tablename__ = "system_config"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Configuration
    key: str = Field(unique=True, max_length=100, description="Config key")
    value: str = Field(description="Config value (JSON string)")
    description: Optional[str] = Field(default=None, description="Config description")
    
    # Metadata
    is_encrypted: bool = Field(default=False, description="Value is encrypted")
    is_system: bool = Field(default=False, description="System-level config (not user-editable)")
    category: str = Field(default="general", max_length=50, description="Config category")
    
    # Validation
    value_type: str = Field(default="string", max_length=20, description="Value type (string, int, bool, json)")
    validation_regex: Optional[str] = Field(default=None, description="Validation regex pattern")