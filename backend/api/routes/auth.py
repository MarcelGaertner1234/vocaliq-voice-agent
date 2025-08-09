"""
VocalIQ Authentication Routes
JWT-basierte Authentifizierung mit Rate-Limiting
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, validator
# from sqlmodel import Session  # TODO: Aktivieren wenn DB implementiert ist

from api.core.config import get_settings
from api.core.security import (
    SecurityManager, 
    get_current_user_token, 
    get_client_ip,
    TokenPayload
)
from api.models.schemas import APIResponse, ErrorResponse
from api.middleware.rate_limiting import strict_rate_limit, medium_rate_limit

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["Authentication"])


class LoginRequest(BaseModel):
    """Login-Request Model"""
    username: str
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    """Login-Response Model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class RefreshTokenRequest(BaseModel):
    """Refresh Token Request"""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Passwort ändern Request"""
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v


class RegisterRequest(BaseModel):
    """Registrierung Request (für Admin)"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    is_active: bool = True
    organization_id: Optional[int] = None
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest
):
    """
    Benutzer-Anmeldung mit JWT-Token
    """
    client_ip = get_client_ip(request)
    
    # Rate-Limiting prüfen
    if not SecurityManager.check_login_attempts(client_ip, login_data.username):
        SecurityManager.record_login_attempt(client_ip, login_data.username, False)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Too many login attempts. Try again in {settings.LOCKOUT_DURATION} seconds."
        )
    
    # TEMPORÄRE ADMIN-ANMELDUNG (bis User-System implementiert ist)
    if (login_data.username == settings.ADMIN_USERNAME and 
        SecurityManager.verify_password(login_data.password, 
                                      SecurityManager.hash_password(settings.ADMIN_PASSWORD))):
        
        # Erfolgreiche Admin-Anmeldung
        SecurityManager.record_login_attempt(client_ip, login_data.username, True)
        
        # Token erstellen
        token_expires = timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * (7 if login_data.remember_me else 1)
        )
        
        access_token = SecurityManager.create_access_token(
            data={
                "sub": login_data.username,
                "user_id": 1,  # Admin-User ID
                "organization_id": 1,  # Default Org
                "scopes": ["admin", "user", "calls", "analytics"]
            },
            expires_delta=token_expires
        )
        
        refresh_token = SecurityManager.create_refresh_token(user_id=1)
        
        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=int(token_expires.total_seconds()),
            user={
                "id": 1,
                "username": settings.ADMIN_USERNAME,
                "email": settings.ADMIN_EMAIL,
                "full_name": "System Administrator",
                "is_active": True,
                "scopes": ["admin", "user", "calls", "analytics"]
            }
        )
    
    # Login fehlgeschlagen
    SecurityManager.record_login_attempt(client_ip, login_data.username, False)
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password"
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    JWT Token mit Refresh Token erneuern
    """
    try:
        # Refresh Token verifizieren
        payload = SecurityManager.verify_token(refresh_data.refresh_token)
        
        if payload.type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Neuen Access Token erstellen
        access_token = SecurityManager.create_access_token(
            data={
                "sub": payload.sub,
                "user_id": payload.user_id,
                "organization_id": payload.organization_id,
                "scopes": payload.scopes
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout(token: TokenPayload = Depends(get_current_user_token)):
    """
    Benutzer abmelden (Token revoken)
    """
    if token.jti:
        SecurityManager.revoke_token(token.jti)
    
    return {"message": "Successfully logged out"}


@router.get("/me")
async def get_current_user(token: TokenPayload = Depends(get_current_user_token)):
    """
    Aktuelle Benutzer-Informationen abrufen
    """
    # TEMPORÄR: Admin-User-Info zurückgeben
    if token.user_id == 1:
        return {
            "id": 1,
            "username": settings.ADMIN_USERNAME,
            "email": settings.ADMIN_EMAIL,
            "full_name": "System Administrator",
            "is_active": True,
            "organization_id": token.organization_id,
            "scopes": token.scopes,
            "last_login": datetime.utcnow().isoformat()
        }
    
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found"
    )


@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    token: TokenPayload = Depends(get_current_user_token)
):
    """
    Passwort ändern (für aktuellen User)
    """
    # TEMPORÄR: Nur für Admin implementiert
    if token.user_id != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to change password"
        )
    
    # Aktuelles Passwort prüfen
    if not SecurityManager.verify_password(
        password_data.current_password,
        SecurityManager.hash_password(settings.ADMIN_PASSWORD)
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Neues Passwort würde hier gespeichert werden
    # Für Demo-Zwecke nur Erfolgsmeldung
    
    return {"message": "Password successfully changed"}


@router.post("/validate-token")
async def validate_token(token: TokenPayload = Depends(get_current_user_token)):
    """
    Token validieren (für Frontend-Checks)
    """
    return {
        "valid": True,
        "user_id": token.user_id,
        "expires": token.exp,
        "scopes": token.scopes
    }


@router.get("/health")
async def auth_health():
    """
    Auth-Service Health Check
    """
    return {
        "status": "healthy",
        "service": "authentication",
        "timestamp": datetime.utcnow().isoformat()
    }