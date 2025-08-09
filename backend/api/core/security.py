"""
VocalIQ Security Module
Implementiert JWT-Authentifizierung, Password-Hashing und API-Key-Verschlüsselung
"""
from datetime import datetime, timedelta
from typing import Optional, Any, Dict
import secrets
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from cryptography.fernet import Fernet
import hashlib
import hmac
import os
from redis import Redis

from api.core.config import get_settings

settings = get_settings()

# Password-Hashing
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=settings.PASSWORD_HASH_ROUNDS
)

# API-Key-Verschlüsselung
encryption_key = settings.ENCRYPTION_KEY.encode()
cipher_suite = Fernet(encryption_key)

# Redis für Session-Management
redis_client = Redis.from_url(settings.REDIS_URL, decode_responses=True)

# HTTP Bearer Token
security = HTTPBearer(auto_error=False)


class TokenPayload(BaseModel):
    """JWT Token Payload"""
    sub: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    jti: Optional[str] = None
    type: str = "access"
    user_id: Optional[int] = None
    organization_id: Optional[int] = None
    scopes: list[str] = []


class LoginAttempt(BaseModel):
    """Login-Versuch für Rate-Limiting"""
    ip_address: str
    username: str
    timestamp: datetime
    success: bool


class SecurityManager:
    """Zentrale Security-Klasse für alle Authentifizierungs-Operationen"""
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any], 
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Erstellt einen JWT Access Token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        # Unique Token ID für Session-Tracking
        jti = secrets.token_urlsafe(32)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "access"
        })
        
        token = jwt.encode(
            to_encode, 
            settings.JWT_SECRET_KEY, 
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Token in Redis für Session-Management speichern
        redis_client.setex(
            f"token:{jti}",
            settings.SESSION_TIMEOUT,
            f"user:{data.get('user_id')}"
        )
        
        return token
    
    @staticmethod
    def create_refresh_token(user_id: int) -> str:
        """Erstellt einen JWT Refresh Token"""
        expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        jti = secrets.token_urlsafe(32)
        
        to_encode = {
            "sub": str(user_id),
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": jti,
            "type": "refresh"
        }
        
        token = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        # Refresh Token mit längerer Gültigkeit speichern
        redis_client.setex(
            f"refresh_token:{jti}",
            settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
            f"user:{user_id}"
        )
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> TokenPayload:
        """Verifiziert und dekodiert einen JWT Token"""
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM]
            )
            
            # Prüfe ob Token in Redis-Session existiert
            jti = payload.get("jti")
            if jti and not redis_client.exists(f"token:{jti}"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token session expired or revoked"
                )
            
            return TokenPayload(**payload)
            
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
    
    @staticmethod
    def revoke_token(jti: str) -> bool:
        """Revoked einen Token (Logout)"""
        return redis_client.delete(f"token:{jti}") > 0
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hasht ein Passwort mit bcrypt"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifiziert ein Passwort gegen Hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def encrypt_api_key(api_key: str) -> str:
        """Verschlüsselt einen API-Key für sichere Speicherung"""
        if not settings.API_KEY_ENCRYPTION:
            return api_key
        
        return cipher_suite.encrypt(api_key.encode()).decode()
    
    @staticmethod
    def decrypt_api_key(encrypted_key: str) -> str:
        """Entschlüsselt einen API-Key"""
        if not settings.API_KEY_ENCRYPTION:
            return encrypted_key
        
        try:
            return cipher_suite.decrypt(encrypted_key.encode()).decode()
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to decrypt API key"
            )
    
    @staticmethod
    def check_login_attempts(ip_address: str, username: str) -> bool:
        """Prüft Rate-Limiting für Login-Versuche"""
        key = f"login_attempts:{ip_address}:{username}"
        attempts = redis_client.get(key)
        
        if attempts and int(attempts) >= settings.MAX_LOGIN_ATTEMPTS:
            return False
        
        return True
    
    @staticmethod
    def record_login_attempt(ip_address: str, username: str, success: bool):
        """Zeichnet einen Login-Versuch auf"""
        key = f"login_attempts:{ip_address}:{username}"
        
        if success:
            # Erfolgreiche Anmeldung - Counter zurücksetzen
            redis_client.delete(key)
        else:
            # Fehlgeschlagene Anmeldung - Counter erhöhen
            current = redis_client.incr(key)
            if current == 1:  # Erste fehlgeschlagene Anmeldung
                redis_client.expire(key, settings.LOCKOUT_DURATION)
    
    @staticmethod
    def generate_api_key(prefix: str = "viq") -> str:
        """Generiert einen neuen API-Key"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"
    
    @staticmethod
    def validate_api_key_format(api_key: str) -> bool:
        """Validiert das Format eines API-Keys"""
        parts = api_key.split("_")
        return len(parts) == 2 and len(parts[1]) >= 32


def get_client_ip(request: Request) -> str:
    """Extrahiert die Client-IP-Adresse"""
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    
    return request.client.host if request.client else "unknown"


async def get_current_user_token(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenPayload:
    """Dependency für aktuellen User aus JWT Token"""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # IP-basierte Rate-Limiting (optional)
    client_ip = get_client_ip(request)
    
    token_payload = SecurityManager.verify_token(credentials.credentials)
    
    if not token_payload.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    return token_payload


def require_scopes(required_scopes: list[str]):
    """Decorator für Scope-basierte Autorisierung"""
    def scope_dependency(token: TokenPayload = Depends(get_current_user_token)):
        if not all(scope in token.scopes for scope in required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required scopes: {required_scopes}"
            )
        return token
    
    return scope_dependency