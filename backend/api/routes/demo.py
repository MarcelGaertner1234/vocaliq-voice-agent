"""
VocalIQ Demo Routes - Database Integration Demonstration
Shows persistent storage working with Users and Organizations
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from api.core.database import get_session
from api.repositories.user_repository import UserRepository
from api.models.database import User, Organization, UserRole, UserStatus
from pydantic import BaseModel, EmailStr

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/demo", tags=["Demo"])


class CreateUserRequest(BaseModel):
    """Demo User Creation Request"""
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    organization_id: Optional[int] = None


class UserSummary(BaseModel):
    """User Summary Response"""
    id: int
    uuid: str
    email: str
    first_name: str
    last_name: str
    status: UserStatus
    role: UserRole
    created_at: str
    organization_id: Optional[int] = None


@router.post("/create-user", response_model=UserSummary)
async def create_demo_user(
    user_data: CreateUserRequest,
    session: AsyncSession = Depends(get_session)
):
    """
    Demo: Create a new user in the database
    Demonstrates persistent storage working
    """
    user_repo = UserRepository(session)
    
    try:
        # Check if user already exists
        existing_user = await user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"User with email {user_data.email} already exists"
            )
        
        # Create new user
        user = await user_repo.create_user(
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            organization_id=user_data.organization_id
        )
        
        logger.info(f"✅ Demo user created: {user.email} (ID: {user.id})")
        
        return UserSummary(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            role=user.role,
            created_at=user.created_at.isoformat(),
            organization_id=user.organization_id
        )
        
    except Exception as e:
        if "already exists" in str(e):
            raise
        logger.error(f"Error creating demo user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )


@router.get("/users", response_model=List[UserSummary])
async def list_demo_users(
    limit: int = 10,
    session: AsyncSession = Depends(get_session)
):
    """
    Demo: List all users from the database
    Demonstrates data retrieval from persistent storage
    """
    user_repo = UserRepository(session)
    
    try:
        users = await user_repo.get_all(limit=limit)
        
        return [
            UserSummary(
                id=user.id,
                uuid=user.uuid,
                email=user.email,
                first_name=user.first_name,
                last_name=user.last_name,
                status=user.status,
                role=user.role,
                created_at=user.created_at.isoformat(),
                organization_id=user.organization_id
            )
            for user in users
        ]
        
    except Exception as e:
        logger.error(f"Error listing demo users: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list users"
        )


@router.get("/users/{user_id}", response_model=UserSummary)
async def get_demo_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Demo: Get a specific user by ID
    Demonstrates single record retrieval
    """
    user_repo = UserRepository(session)
    
    try:
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        return UserSummary(
            id=user.id,
            uuid=user.uuid,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            status=user.status,
            role=user.role,
            created_at=user.created_at.isoformat(),
            organization_id=user.organization_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting demo user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user"
        )


@router.get("/user-stats")
async def get_user_statistics(
    session: AsyncSession = Depends(get_session)
):
    """
    Demo: Get user statistics from the database
    Demonstrates aggregation queries
    """
    user_repo = UserRepository(session)
    
    try:
        stats = await user_repo.get_user_statistics()
        return {
            "database_status": "✅ Connected and working",
            "persistent_storage": "✅ Functional",
            "statistics": stats,
            "demo_complete": "🎉 VocalIQ database integration successful!"
        }
        
    except Exception as e:
        logger.error(f"Error getting user stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user statistics"
        )


@router.delete("/users/{user_id}")
async def delete_demo_user(
    user_id: int,
    session: AsyncSession = Depends(get_session)
):
    """
    Demo: Delete a user from the database
    Demonstrates data deletion
    """
    user_repo = UserRepository(session)
    
    try:
        # Check if user exists first
        user = await user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        
        # Delete the user
        success = await user_repo.delete(user_id)
        if success:
            logger.info(f"🗑️ Demo user deleted: ID {user_id}")
            return {"message": f"User {user_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting demo user {user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user"
        )