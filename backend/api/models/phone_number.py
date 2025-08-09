"""
Phone Number Models for Managing Company Phone Numbers
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
from enum import Enum
import uuid

class PhoneNumberType(str, Enum):
    """Type of phone number"""
    TWILIO = "twilio"
    BYOD = "byod"  # Bring Your Own Device
    VIRTUAL = "virtual"

class PhoneNumberStatus(str, Enum):
    """Status of phone number"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"

class PhoneNumber(SQLModel, table=True):
    """
    Phone Number model for managing company phone numbers
    """
    __tablename__ = "phone_numbers"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    number: str = Field(index=True, unique=True)
    type: PhoneNumberType = Field(default=PhoneNumberType.TWILIO)
    status: PhoneNumberStatus = Field(default=PhoneNumberStatus.ACTIVE)
    
    # Company assignment
    company_id: Optional[str] = Field(default=None, foreign_key="companies.id", index=True)
    purpose: Optional[str] = None  # Main Support, Sales, etc.
    assigned_to: Optional[str] = None  # Specific user assignment
    
    # Twilio specific
    twilio_sid: Optional[str] = None
    twilio_capabilities: Optional[dict] = Field(default=None, sa_column_kwargs={"type": "json"})
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    company: Optional["Company"] = Relationship(back_populates="phone_numbers")

class PhoneNumberCreate(SQLModel):
    """Schema for creating a phone number"""
    number: str
    type: PhoneNumberType = PhoneNumberType.TWILIO
    status: PhoneNumberStatus = PhoneNumberStatus.ACTIVE
    company_id: Optional[str] = None
    purpose: Optional[str] = None
    assigned_to: Optional[str] = None

class PhoneNumberUpdate(SQLModel):
    """Schema for updating a phone number"""
    number: Optional[str] = None
    type: Optional[PhoneNumberType] = None
    status: Optional[PhoneNumberStatus] = None
    company_id: Optional[str] = None
    purpose: Optional[str] = None
    assigned_to: Optional[str] = None

class PhoneNumberResponse(SQLModel):
    """Schema for phone number response"""
    id: str
    number: str
    type: PhoneNumberType
    status: PhoneNumberStatus
    company_id: Optional[str]
    company_name: Optional[str] = None
    purpose: Optional[str]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime