"""
VocalIQ Configuration Management
Zentrale Konfiguration mit Pydantic Settings
"""
from functools import lru_cache
from typing import Optional, List
from pydantic_settings import BaseSettings
from pydantic import Field, validator


class Settings(BaseSettings):
    """Hauptkonfiguration für VocalIQ"""
    
    # Core Settings
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    LOG_LEVEL: str = Field(default="INFO")
    SECRET_KEY: str = Field(default="change-this-secret-key-in-production-min-32-chars")
    TIMEZONE: str = Field(default="Europe/Berlin")
    DEFAULT_LANGUAGE: str = Field(default="de")
    
    # API Configuration
    API_BASE_URL: str = Field(default="http://localhost:8000")
    FRONTEND_URL: str = Field(default="http://localhost:5173")
    ALLOWED_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")
    API_VERSION: str = Field(default="v1")
    REQUEST_TIMEOUT: int = Field(default=30)
    MAX_REQUEST_SIZE: int = Field(default=50)
    DEFAULT_PAGE_SIZE: int = Field(default=20)
    MAX_PAGE_SIZE: int = Field(default=100)
    
    # Database
    DATABASE_URL: str = Field(default="postgresql://vocaliq:vocaliq_secure_2024@localhost:5432/vocaliq")
    DATABASE_HOST: str = Field(default="localhost")
    DATABASE_PORT: int = Field(default=5432)
    DATABASE_NAME: str = Field(default="vocaliq")
    DATABASE_USER: str = Field(default="vocaliq")
    DATABASE_PASSWORD: str = Field(default="vocaliq_secure_2024")
    DATABASE_POOL_SIZE: int = Field(default=20)
    DATABASE_MAX_OVERFLOW: int = Field(default=0)
    DATABASE_POOL_TIMEOUT: int = Field(default=30)
    DATABASE_POOL_RECYCLE: int = Field(default=3600)
    DATABASE_ECHO: bool = Field(default=False)
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")
    REDIS_PASSWORD: Optional[str] = Field(default=None)
    REDIS_SSL: bool = Field(default=False)
    REDIS_MAX_CONNECTIONS: int = Field(default=50)
    CACHE_DEFAULT_TIMEOUT: int = Field(default=300)
    CACHE_KEY_PREFIX: str = Field(default="vocaliq")
    
    # Authentication
    JWT_SECRET_KEY: str = Field(default="change-this-secret-key-in-production-min-32-chars")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7)
    ADMIN_USERNAME: str = Field(default="admin")
    ADMIN_PASSWORD: str = Field(default="vocaliq2024")
    ADMIN_EMAIL: str = Field(default="admin@vocaliq.de")
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = Field(default=None)
    TWILIO_AUTH_TOKEN: Optional[str] = Field(default=None)
    TWILIO_PHONE_NUMBER: Optional[str] = Field(default=None)
    TWILIO_WEBHOOK_URL: Optional[str] = Field(default=None)
    TWILIO_STATUS_CALLBACK_URL: Optional[str] = Field(default=None)
    TWILIO_WEBHOOK_VALIDATE: bool = Field(default=True)
    TWILIO_MAX_CALL_DURATION: int = Field(default=3600)
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = Field(default=None)
    OPENAI_ORGANIZATION: Optional[str] = Field(default=None)
    OPENAI_MODEL: str = Field(default="gpt-4-turbo-preview")
    OPENAI_TEMPERATURE: float = Field(default=0.7)
    OPENAI_MAX_TOKENS: int = Field(default=2000)
    WHISPER_MODEL: str = Field(default="whisper-1")
    WHISPER_LANGUAGE: str = Field(default="de")
    
    # ElevenLabs
    ELEVENLABS_API_KEY: Optional[str] = Field(default=None)
    ELEVENLABS_VOICE_ID: str = Field(default="21m00Tcm4TlvDq8ikWAM")
    ELEVENLABS_MODEL: str = Field(default="eleven_multilingual_v2")
    ELEVENLABS_VOICE_SETTINGS_STABILITY: float = Field(default=0.5)
    ELEVENLABS_VOICE_SETTINGS_SIMILARITY_BOOST: float = Field(default=0.75)
    
    # Weaviate
    WEAVIATE_URL: str = Field(default="http://localhost:8081")
    WEAVIATE_API_KEY: Optional[str] = Field(default=None)
    WEAVIATE_SCHEMA_NAME: str = Field(default="VocalIQKnowledge")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True)
    RATE_LIMIT_GENERAL: str = Field(default="100/minute")
    RATE_LIMIT_AUDIO: str = Field(default="20/minute")
    RATE_LIMIT_CALLS: str = Field(default="10/minute")
    
    # Security
    CORS_ALLOW_CREDENTIALS: bool = Field(default=True)
    SECURE_COOKIES: bool = Field(default=False)
    SESSION_COOKIE_HTTPONLY: bool = Field(default=True)
    SESSION_COOKIE_SAMESITE: str = Field(default="lax")
    ENCRYPTION_KEY: str = Field(default="AaI_ztaXR8wdefR80ML6zZGJkp3YkxBQqJEuymKhCoo=")
    PASSWORD_HASH_ROUNDS: int = Field(default=12)
    SESSION_TIMEOUT: int = Field(default=3600)
    MAX_LOGIN_ATTEMPTS: int = Field(default=5)
    LOCKOUT_DURATION: int = Field(default=900)
    API_KEY_ENCRYPTION: bool = Field(default=True)
    
    # Feature Flags
    FEATURE_OUTBOUND_CALLS: bool = Field(default=True)
    FEATURE_INBOUND_CALLS: bool = Field(default=True)
    FEATURE_CALENDAR_INTEGRATION: bool = Field(default=True)
    FEATURE_CRM_INTEGRATION: bool = Field(default=True)
    FEATURE_ANALYTICS: bool = Field(default=True)
    FEATURE_MULTI_TENANT: bool = Field(default=True)
    FEATURE_WEBHOOKS: bool = Field(default=True)
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = Field(default=False)
    PROMETHEUS_PORT: int = Field(default=9090)
    GRAFANA_ENABLED: bool = Field(default=False)
    GRAFANA_PORT: int = Field(default=3000)
    SENTRY_ENABLED: bool = Field(default=False)
    SENTRY_DSN: Optional[str] = Field(default=None)
    
    # Storage
    STORAGE_TYPE: str = Field(default="local")
    STORAGE_LOCAL_PATH: str = Field(default="./storage")
    UPLOAD_MAX_SIZE: str = Field(default="50MB")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"
    
    @validator('ALLOWED_ORIGINS')
    def parse_cors_origins(cls, v):
        """Parse CORS origins from comma-separated string to list"""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',')]
        return v
    
    @validator('PASSWORD_HASH_ROUNDS')
    def validate_hash_rounds(cls, v):
        """Validate bcrypt rounds (4-15 for security/performance balance)"""
        if not 4 <= v <= 15:
            raise ValueError('PASSWORD_HASH_ROUNDS must be between 4 and 15')
        return v
    
    @validator('JWT_ACCESS_TOKEN_EXPIRE_MINUTES')
    def validate_token_expiry(cls, v):
        """Validate token expiry time"""
        if v <= 0:
            raise ValueError('JWT_ACCESS_TOKEN_EXPIRE_MINUTES must be positive')
        if v > 1440:  # 24 hours
            raise ValueError('JWT_ACCESS_TOKEN_EXPIRE_MINUTES should not exceed 24 hours for security')
        return v
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Get CORS origins as list"""
        if isinstance(self.ALLOWED_ORIGINS, str):
            return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(',')]
        return self.ALLOWED_ORIGINS
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"
    
    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (replace asyncpg with psycopg2)"""
        if self.DATABASE_URL.startswith("postgresql+asyncpg://"):
            return self.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://")
        return self.DATABASE_URL


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()