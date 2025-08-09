"""
VocalIQ Pydantic Schemas für Input-Validation
Umfassende Validierung aller API-Eingaben
"""
from datetime import datetime
from typing import Optional, List, Dict, Any, Union
from enum import Enum
from pydantic import (
    BaseModel, 
    Field, 
    validator, 
    root_validator,
    EmailStr,
    constr,
    conint,
    confloat
)
import re
import phonenumbers
from phonenumbers import NumberParseException


class CallStatus(str, Enum):
    """Call Status Enum"""
    INITIATED = "initiated"
    RINGING = "ringing"
    ANSWERED = "answered"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no-answer"
    CANCELLED = "cancelled"


class CallDirection(str, Enum):
    """Call Direction Enum"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class AudioFormat(str, Enum):
    """Supported Audio Formats"""
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    WEBM = "webm"


class Language(str, Enum):
    """Supported Languages"""
    DE = "de"
    EN = "en"
    ES = "es"
    FR = "fr"
    IT = "it"


# Base Schemas
class TimestampMixin(BaseModel):
    """Mixin für Timestamps"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class PaginationParams(BaseModel):
    """Pagination Parameters"""
    page: conint(ge=1) = Field(default=1, description="Page number (1-based)")
    size: conint(ge=1, le=100) = Field(default=20, description="Items per page")
    sort_by: Optional[str] = Field(default="created_at", description="Sort field")
    sort_order: Optional[str] = Field(default="desc", pattern="^(asc|desc)$")


class PhoneNumberStr(str):
    """Custom Phone Number Validation"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError('string required')
        
        try:
            # Parse phone number
            number = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(number):
                raise ValueError('Invalid phone number')
            
            # Return in international format
            return phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.E164)
        except NumberParseException:
            raise ValueError('Invalid phone number format')


# Call Management Schemas
class CallRequest(BaseModel):
    """Outbound Call Request"""
    to_number: PhoneNumberStr = Field(..., description="Destination phone number")
    from_number: Optional[PhoneNumberStr] = Field(None, description="Source number (optional)")
    message: constr(min_length=1, max_length=5000) = Field(..., description="Message to speak")
    voice_id: Optional[str] = Field(None, description="ElevenLabs voice ID")
    language: Language = Field(default=Language.DE, description="Language for TTS")
    max_duration: conint(ge=30, le=3600) = Field(default=300, description="Max call duration in seconds")
    webhook_url: Optional[str] = Field(None, description="Webhook for call events")
    
    @validator('webhook_url')
    def validate_webhook_url(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValueError('Webhook URL must start with http:// or https://')
        return v


class CallResponse(TimestampMixin):
    """Call Response Model"""
    id: str = Field(..., description="Unique call ID")
    status: CallStatus
    direction: CallDirection
    from_number: str
    to_number: str
    duration: Optional[int] = Field(None, description="Call duration in seconds")
    cost: Optional[float] = Field(None, description="Call cost")
    recording_url: Optional[str] = None
    transcript: Optional[str] = None
    error_message: Optional[str] = None


class CallUpdate(BaseModel):
    """Call Status Update"""
    status: CallStatus
    duration: Optional[int] = None
    error_message: Optional[str] = None


# Audio Processing Schemas
class AudioUpload(BaseModel):
    """Audio Upload Request"""
    format: AudioFormat = Field(..., description="Audio format")
    sample_rate: conint(ge=8000, le=48000) = Field(default=16000)
    channels: conint(ge=1, le=2) = Field(default=1)
    duration: Optional[confloat(gt=0, le=3600)] = Field(None, description="Duration in seconds")


class TranscriptionRequest(BaseModel):
    """Speech-to-Text Request"""
    audio_url: str = Field(..., description="URL to audio file")
    language: Language = Field(default=Language.DE)
    model: str = Field(default="whisper-1")
    
    @validator('audio_url')
    def validate_audio_url(cls, v):
        if not v.startswith(('http://', 'https://', 'file://')):
            raise ValueError('Audio URL must be a valid URL')
        return v


class TranscriptionResponse(BaseModel):
    """Speech-to-Text Response"""
    transcript: str
    confidence: confloat(ge=0.0, le=1.0)
    language: str
    duration: float
    word_count: int


class TTSRequest(BaseModel):
    """Text-to-Speech Request"""
    text: constr(min_length=1, max_length=5000) = Field(..., description="Text to synthesize")
    voice_id: str = Field(..., description="ElevenLabs voice ID")
    language: Language = Field(default=Language.DE)
    stability: confloat(ge=0.0, le=1.0) = Field(default=0.5)
    similarity_boost: confloat(ge=0.0, le=1.0) = Field(default=0.75)
    style: confloat(ge=0.0, le=1.0) = Field(default=0.0)
    
    @validator('text')
    def validate_text_content(cls, v):
        # Remove excessive whitespace
        v = re.sub(r'\s+', ' ', v).strip()
        
        # Check for potentially harmful content
        forbidden_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'data:text/html'
        ]
        
        for pattern in forbidden_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError('Text contains potentially harmful content')
        
        return v


class TTSResponse(BaseModel):
    """Text-to-Speech Response"""
    audio_url: str
    duration: float
    format: str = "mp3"
    sample_rate: int = 22050


# AI Conversation Schemas
class ConversationRequest(BaseModel):
    """AI Conversation Request"""
    message: constr(min_length=1, max_length=2000) = Field(..., description="User message")
    context: Optional[List[Dict[str, str]]] = Field(default=[], description="Conversation history")
    system_prompt: Optional[str] = Field(None, description="Custom system prompt")
    temperature: confloat(ge=0.0, le=2.0) = Field(default=0.7)
    max_tokens: conint(ge=1, le=4000) = Field(default=1000)
    
    @validator('context')
    def validate_context(cls, v):
        if len(v) > 20:  # Limit context history
            v = v[-20:]  # Keep only last 20 messages
        
        for msg in v:
            if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                raise ValueError('Context messages must have "role" and "content" fields')
            if msg['role'] not in ['user', 'assistant', 'system']:
                raise ValueError('Invalid message role')
        
        return v


class ConversationResponse(BaseModel):
    """AI Conversation Response"""
    message: str
    usage: Dict[str, int]
    model: str
    finish_reason: str


# User Management Schemas
class UserCreate(BaseModel):
    """User Creation Request"""
    username: constr(pattern=r'^[a-zA-Z0-9_]{3,20}$') = Field(..., description="Username (3-20 chars, alphanumeric + underscore)")
    email: EmailStr
    password: constr(min_length=8, max_length=128) = Field(..., description="Password (min 8 chars)")
    full_name: Optional[str] = Field(None, max_length=100)
    phone_number: Optional[PhoneNumberStr] = None
    organization_id: Optional[int] = None
    
    @validator('password')
    def validate_password_strength(cls, v):
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v


class UserUpdate(BaseModel):
    """User Update Request"""
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[EmailStr] = None
    phone_number: Optional[PhoneNumberStr] = None
    is_active: Optional[bool] = None


class UserResponse(TimestampMixin):
    """User Response Model"""
    id: int
    username: str
    email: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool
    last_login: Optional[datetime] = None
    organization_id: Optional[int] = None


# Organization Schemas
class OrganizationCreate(BaseModel):
    """Organization Creation Request"""
    name: constr(min_length=2, max_length=100) = Field(..., description="Organization name")
    domain: Optional[str] = Field(None, description="Email domain for auto-assignment")
    phone_number: Optional[PhoneNumberStr] = None
    address: Optional[str] = Field(None, max_length=500)
    
    @validator('domain')
    def validate_domain(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid domain format')
        return v


class OrganizationResponse(TimestampMixin):
    """Organization Response Model"""
    id: int
    name: str
    domain: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    user_count: int = 0
    call_count: int = 0


# Webhook Schemas
class WebhookEvent(BaseModel):
    """Generic Webhook Event"""
    event_type: str = Field(..., description="Type of event")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(..., description="Event payload")
    signature: Optional[str] = Field(None, description="HMAC signature for verification")


class CallWebhookEvent(WebhookEvent):
    """Call-specific Webhook Event"""
    call_id: str
    status: CallStatus
    direction: CallDirection
    from_number: str
    to_number: str
    duration: Optional[int] = None


# Analytics Schemas
class AnalyticsQuery(BaseModel):
    """Analytics Query Parameters"""
    start_date: datetime = Field(..., description="Start date for analytics")
    end_date: datetime = Field(..., description="End date for analytics")
    organization_id: Optional[int] = None
    metrics: List[str] = Field(default=["call_count", "success_rate", "avg_duration"])
    group_by: Optional[str] = Field(default="day", pattern="^(hour|day|week|month)$")
    
    @validator('end_date')
    def validate_date_range(cls, v, values):
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class AnalyticsResponse(BaseModel):
    """Analytics Response"""
    period: str
    metrics: Dict[str, Union[int, float]]
    data: List[Dict[str, Any]]


# API Response Wrapper
class APIResponse(BaseModel):
    """Standard API Response Wrapper"""
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    errors: Optional[List[str]] = None
    meta: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    """Error Response Model"""
    success: bool = False
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Validation Helper Functions
def validate_file_size(file_size: int, max_size_mb: int = 50) -> bool:
    """Validate file size"""
    return file_size <= max_size_mb * 1024 * 1024


def validate_audio_format(filename: str) -> bool:
    """Validate audio file format"""
    allowed_extensions = {'.wav', '.mp3', '.ogg', '.webm', '.m4a'}
    return any(filename.lower().endswith(ext) for ext in allowed_extensions)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove path separators and dangerous chars
    filename = re.sub(r'[/\\<>:"|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:250] + ('.' + ext if ext else '')
    
    return filename


def validate_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Validate webhook signature"""
    import hmac
    import hashlib
    
    expected_signature = hmac.new(
        secret.encode('utf-8'),
        payload.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)