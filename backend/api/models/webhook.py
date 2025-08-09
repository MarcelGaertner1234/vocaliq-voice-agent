"""
Webhook Models for External Integrations
"""

from sqlmodel import SQLModel, Field, Column, JSON
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class WebhookStatus(str, Enum):
    """Status of webhook"""
    ACTIVE = "active"
    INACTIVE = "inactive"

class WebhookEvent(str, Enum):
    """Available webhook events"""
    CALL_STARTED = "call.started"
    CALL_ENDED = "call.ended"
    CALL_FAILED = "call.failed"
    AGENT_ERROR = "agent.error"
    TRANSCRIPT_READY = "transcript.ready"
    RECORDING_READY = "recording.ready"
    USER_CREATED = "user.created"
    USER_UPDATED = "user.updated"
    COMPANY_UPDATED = "company.updated"

class Webhook(SQLModel, table=True):
    """
    Webhook model for external integrations
    """
    __tablename__ = "webhooks"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    name: str = Field(index=True)
    url: str
    events: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: WebhookStatus = Field(default=WebhookStatus.ACTIVE)
    
    # Company assignment
    company_id: Optional[str] = Field(default=None, foreign_key="companies.id", index=True)
    
    # Configuration
    headers: Dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    retry_count: int = Field(default=3)
    timeout_seconds: int = Field(default=30)
    
    # Statistics
    last_triggered: Optional[datetime] = None
    success_count: int = Field(default=0)
    failure_count: int = Field(default=0)
    
    @property
    def success_rate(self) -> float:
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        return (self.success_count / total) * 100
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WebhookCreate(SQLModel):
    """Schema for creating a webhook"""
    name: str
    url: str
    events: List[str]
    status: WebhookStatus = WebhookStatus.ACTIVE
    company_id: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    retry_count: Optional[int] = 3
    timeout_seconds: Optional[int] = 30

class WebhookUpdate(SQLModel):
    """Schema for updating a webhook"""
    name: Optional[str] = None
    url: Optional[str] = None
    events: Optional[List[str]] = None
    status: Optional[WebhookStatus] = None
    headers: Optional[Dict[str, str]] = None
    retry_count: Optional[int] = None
    timeout_seconds: Optional[int] = None

class WebhookResponse(SQLModel):
    """Schema for webhook response"""
    id: str
    name: str
    url: str
    events: List[str]
    status: WebhookStatus
    company_id: Optional[str]
    headers: Dict[str, str]
    last_triggered: Optional[datetime]
    success_rate: float
    created_at: datetime
    updated_at: datetime

class WebhookTestRequest(SQLModel):
    """Schema for testing a webhook"""
    payload: Optional[Dict[str, Any]] = None

class WebhookLog(SQLModel, table=True):
    """
    Webhook execution log
    """
    __tablename__ = "webhook_logs"
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    webhook_id: str = Field(foreign_key="webhooks.id", index=True)
    
    event: str
    payload: Dict[str, Any] = Field(sa_column=Column(JSON))
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None
    
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: Optional[int] = None
    success: bool = Field(default=False)