"""
Users API Routes - Extended with CRUD operations
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext

from ..database import get_session
from ..auth import get_current_user
from pydantic import BaseModel, EmailStr

router = APIRouter(prefix="/api/users", tags=["Users"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(str):
    """User roles"""
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    CUSTOMER = "customer"

class UserStatus(str):
    """User status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

class UserCreate(BaseModel):
    """Schema for creating a user"""
    email: EmailStr
    password: str
    name: str
    role: str = UserRole.CUSTOMER
    company_id: Optional[str] = None
    status: str = UserStatus.ACTIVE

class UserUpdate(BaseModel):
    """Schema for updating a user"""
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    role: Optional[str] = None
    company_id: Optional[str] = None
    status: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    name: str
    role: str
    company_id: Optional[str]
    company_name: Optional[str] = None
    status: str
    created_at: Optional[datetime]
    last_login: Optional[datetime] = None

# Simple in-memory user storage for demo (in production, use database)
demo_users = [
    {
        "id": "1",
        "email": "admin@vocaliq.de",
        "name": "Admin User",
        "role": UserRole.ADMIN,
        "company_id": None,
        "status": UserStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "password_hash": pwd_context.hash("admin123")
    },
    {
        "id": "2",
        "email": "max@techcorp.de",
        "name": "Max Mustermann",
        "role": UserRole.MANAGER,
        "company_id": "company-1",
        "status": UserStatus.ACTIVE,
        "created_at": datetime.utcnow(),
        "password_hash": pwd_context.hash("password123")
    }
]

@router.get("/", response_model=List[UserResponse])
async def get_users(
    current_user: dict = Depends(get_current_user)
):
    """Get all users (Admin only)"""
    if current_user.get("role") != "admin":
        # Non-admin users can only see users from their company
        company_id = current_user.get("company_id")
        filtered_users = [u for u in demo_users if u.get("company_id") == company_id]
    else:
        filtered_users = demo_users
    
    # Remove password hash from response
    response = []
    for user in filtered_users:
        user_dict = {k: v for k, v in user.items() if k != "password_hash"}
        # Add mock company name
        if user_dict.get("company_id"):
            user_dict["company_name"] = "TechCorp GmbH"  # Mock
        response.append(UserResponse(**user_dict))
    
    return response

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific user"""
    user = next((u for u in demo_users if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access rights
    if current_user.get("role") != "admin":
        if user_id != current_user.get("id") and user.get("company_id") != current_user.get("company_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    user_dict = {k: v for k, v in user.items() if k != "password_hash"}
    if user_dict.get("company_id"):
        user_dict["company_name"] = "TechCorp GmbH"  # Mock
    
    return UserResponse(**user_dict)

@router.post("/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new user (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # Check if email already exists
    existing = next((u for u in demo_users if u["email"] == user_data.email), None)
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = {
        "id": str(len(demo_users) + 1),
        "email": user_data.email,
        "name": user_data.name,
        "role": user_data.role,
        "company_id": user_data.company_id,
        "status": user_data.status,
        "created_at": datetime.utcnow(),
        "password_hash": pwd_context.hash(user_data.password)
    }
    
    demo_users.append(new_user)
    
    user_dict = {k: v for k, v in new_user.items() if k != "password_hash"}
    if user_dict.get("company_id"):
        user_dict["company_name"] = "TechCorp GmbH"  # Mock
    
    return UserResponse(**user_dict)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a user"""
    user = next((u for u in demo_users if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access rights
    if current_user.get("role") != "admin":
        if user_id != current_user.get("id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    # Update fields
    update_data = user_update.dict(exclude_unset=True)
    
    # Hash password if provided
    if "password" in update_data:
        user["password_hash"] = pwd_context.hash(update_data.pop("password"))
    
    # Update other fields
    for field, value in update_data.items():
        if field in user:
            user[field] = value
    
    user_dict = {k: v for k, v in user.items() if k != "password_hash"}
    if user_dict.get("company_id"):
        user_dict["company_name"] = "TechCorp GmbH"  # Mock
    
    return UserResponse(**user_dict)

@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a user (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    user_index = next((i for i, u in enumerate(demo_users) if u["id"] == user_id), None)
    
    if user_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Don't allow deleting the last admin
    user = demo_users[user_index]
    if user["role"] == UserRole.ADMIN:
        admin_count = sum(1 for u in demo_users if u["role"] == UserRole.ADMIN)
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the last admin user"
            )
    
    demo_users.pop(user_index)
    
    return {"message": "User deleted successfully"}

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: str,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """Reset user password (Admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    user = next((u for u in demo_users if u["id"] == user_id), None)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user["password_hash"] = pwd_context.hash(new_password)
    
    return {"message": "Password reset successfully"}

@router.get("/company/{company_id}", response_model=List[UserResponse])
async def get_company_users(
    company_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all users for a specific company"""
    # Check access rights
    if current_user.get("role") != "admin" and company_id != current_user.get("company_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    company_users = [u for u in demo_users if u.get("company_id") == company_id]
    
    response = []
    for user in company_users:
        user_dict = {k: v for k, v in user.items() if k != "password_hash"}
        user_dict["company_name"] = "TechCorp GmbH"  # Mock
        response.append(UserResponse(**user_dict))
    
    return response