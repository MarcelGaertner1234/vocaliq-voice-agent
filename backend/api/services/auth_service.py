"""
Authentication Service
Provides user authentication and authorization functions
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from jose import JWTError, jwt

from api.core.config import get_settings
from api.core.database import get_session
from api.core.security import SecurityManager, get_current_user_token, TokenPayload
from api.models.auth import User
from api.models.company import Company

settings = get_settings()


async def get_current_user(
    token: TokenPayload = Depends(get_current_user_token)
) -> User:
    """
    Get current authenticated user from token
    """
    async with get_session() as session:
        # For now, return a mock user for admin
        if token.user_id == 1:  # Admin user
            admin_user = User(
                id=1,
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                full_name="System Administrator",
                is_active=True,
                is_superuser=True,
                organization_id=1,
                role="admin"
            )
            return admin_user
        
        # Try to get user from database
        result = await session.execute(
            select(User).where(User.id == token.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user


async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they have admin privileges
    """
    # Check if user is admin (either by role or superuser flag)
    is_admin = (
        current_user.role == "admin" or 
        current_user.is_superuser or
        (hasattr(current_user, 'scopes') and 'admin' in current_user.scopes)
    )
    
    if not is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    
    return current_user


async def get_current_customer_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they have customer privileges
    """
    # Customers can be any authenticated user
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is not active"
        )
    
    return current_user


async def get_user_company(
    current_user: User = Depends(get_current_user)
) -> Optional[Company]:
    """
    Get the company associated with the current user
    """
    if not current_user.organization_id:
        return None
    
    async with get_session() as session:
        company = await session.get(Company, current_user.organization_id)
        return company


async def verify_user_company_access(
    company_id: str,
    current_user: User = Depends(get_current_user)
) -> bool:
    """
    Verify that the current user has access to the specified company
    """
    # Admins have access to all companies
    if current_user.role == "admin" or current_user.is_superuser:
        return True
    
    # Other users only have access to their own company
    if str(current_user.organization_id) == str(company_id):
        return True
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You don't have access to this company"
    )


async def create_user(
    username: str,
    email: str,
    password: str,
    full_name: Optional[str] = None,
    organization_id: Optional[int] = None,
    role: str = "customer"
) -> User:
    """
    Create a new user
    """
    async with get_session() as session:
        # Check if user already exists
        existing_user = await session.execute(
            select(User).where(
                (User.username == username) | (User.email == email)
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this username or email already exists"
            )
        
        # Hash password
        hashed_password = SecurityManager.hash_password(password)
        
        # Create user
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            organization_id=organization_id,
            role=role,
            is_active=True,
            is_superuser=(role == "admin")
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return user


async def authenticate_user(username: str, password: str) -> Optional[User]:
    """
    Authenticate a user with username and password
    """
    async with get_session() as session:
        # Get user by username or email
        result = await session.execute(
            select(User).where(
                (User.username == username) | (User.email == username)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Verify password
        if not SecurityManager.verify_password(password, user.hashed_password):
            return None
        
        if not user.is_active:
            return None
        
        return user


async def update_user_password(
    user_id: int,
    current_password: str,
    new_password: str
) -> bool:
    """
    Update user password
    """
    async with get_session() as session:
        user = await session.get(User, user_id)
        
        if not user:
            return False
        
        # Verify current password
        if not SecurityManager.verify_password(current_password, user.hashed_password):
            return False
        
        # Update password
        user.hashed_password = SecurityManager.hash_password(new_password)
        session.add(user)
        await session.commit()
        
        return True