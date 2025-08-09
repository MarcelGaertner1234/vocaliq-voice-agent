"""
User Repository für VocalIQ
Datenzugriff für User-Entities
"""
import logging
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from passlib.context import CryptContext

from api.models.database import User, UserStatus
from api.repositories.base import BaseRepository

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserRepository(BaseRepository[User]):
    """Repository für User-Entity"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.session.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def create_user(
        self, 
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        organization_id: Optional[int] = None,
        **kwargs
    ) -> User:
        """Create new user with password hashing"""
        # Hash password
        password_hash = pwd_context.hash(password)
        
        user_data = {
            "email": email,
            "password_hash": password_hash,
            "first_name": first_name,
            "last_name": last_name,
            "organization_id": organization_id,
            **kwargs
        }
        
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        
        logger.info(f"👤 Created user: {email}")
        return user
    
    async def verify_password(self, user: User, password: str) -> bool:
        """Verify user password"""
        return pwd_context.verify(password, user.password_hash)
    
    async def update_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        password_hash = pwd_context.hash(new_password)
        
        result = await self.update(user_id, {"password_hash": password_hash})
        
        if result:
            logger.info(f"🔐 Password updated for user ID: {user_id}")
            return True
        return False
    
    async def get_users_by_organization(
        self, 
        organization_id: int,
        status: Optional[UserStatus] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Get users by organization"""
        query = select(User).where(User.organization_id == organization_id)
        
        if status:
            query = query.where(User.status == status)
        
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def search_users(
        self, 
        search_term: str,
        organization_id: Optional[int] = None,
        offset: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by email, name, or username"""
        search_pattern = f"%{search_term.lower()}%"
        
        query = select(User).where(
            or_(
                User.email.ilike(search_pattern),
                User.first_name.ilike(search_pattern),
                User.last_name.ilike(search_pattern),
                User.username.ilike(search_pattern)
            )
        )
        
        if organization_id:
            query = query.where(User.organization_id == organization_id)
        
        query = query.offset(offset).limit(limit).order_by(User.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update_last_login(self, user_id: int):
        """Update user's last login timestamp"""
        from datetime import datetime, timezone
        
        # Get current user first
        user = await self.get_by_id(user_id)
        if user:
            await self.update(user_id, {
                "last_login_at": datetime.now(timezone.utc),
                "last_active_at": datetime.now(timezone.utc),
                "login_count": user.login_count + 1
            })
    
    async def update_last_active(self, user_id: int):
        """Update user's last active timestamp"""
        from datetime import datetime, timezone
        
        await self.update(user_id, {
            "last_active_at": datetime.now(timezone.utc)
        })
    
    async def get_active_users(
        self,
        organization_id: Optional[int] = None,
        minutes: int = 15
    ) -> List[User]:
        """Get users active in the last N minutes"""
        from datetime import datetime, timezone, timedelta
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        
        query = select(User).where(
            and_(
                User.status == UserStatus.ACTIVE,
                User.last_active_at >= cutoff_time
            )
        )
        
        if organization_id:
            query = query.where(User.organization_id == organization_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate user account"""
        result = await self.update(user_id, {"status": UserStatus.INACTIVE})
        if result:
            logger.info(f"🚫 Deactivated user ID: {user_id}")
            return True
        return False
    
    async def activate_user(self, user_id: int) -> bool:
        """Activate user account"""
        result = await self.update(user_id, {"status": UserStatus.ACTIVE})
        if result:
            logger.info(f"✅ Activated user ID: {user_id}")
            return True
        return False
    
    async def verify_email(self, user_id: int) -> bool:
        """Mark user email as verified"""
        from datetime import datetime, timezone
        
        result = await self.update(user_id, {
            "is_verified": True,
            "email_verified_at": datetime.now(timezone.utc)
        })
        
        if result:
            logger.info(f"📧 Email verified for user ID: {user_id}")
            return True
        return False
    
    async def get_user_statistics(self, organization_id: Optional[int] = None) -> Dict[str, Any]:
        """Get user statistics"""
        from sqlalchemy import func
        
        base_query = select(func.count(User.id))
        if organization_id:
            base_query = base_query.where(User.organization_id == organization_id)
        
        # Total users
        total_result = await self.session.execute(base_query)
        total_users = total_result.scalar()
        
        # Active users
        active_query = base_query.where(User.status == UserStatus.ACTIVE)
        active_result = await self.session.execute(active_query)
        active_users = active_result.scalar()
        
        # Verified users
        verified_query = base_query.where(User.is_verified == True)
        verified_result = await self.session.execute(verified_query)
        verified_users = verified_result.scalar()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "verified_users": verified_users,
            "unverified_users": total_users - verified_users,
            "verification_rate": round(verified_users / total_users * 100, 1) if total_users > 0 else 0
        }