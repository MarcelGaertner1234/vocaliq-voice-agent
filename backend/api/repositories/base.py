"""
Base Repository Pattern für VocalIQ
Abstrakte Basis-Klasse für alle Repository-Implementierungen
"""
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType], ABC):
    """Base Repository mit CRUD Operations"""
    
    def __init__(self, session: AsyncSession, model: type[ModelType]):
        self.session = session
        self.model = model
    
    async def create(self, obj_data: Dict[str, Any]) -> ModelType:
        """Create new entity"""
        obj = self.model(**obj_data)
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
    
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        """Get entity by ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_uuid(self, uuid: str) -> Optional[ModelType]:
        """Get entity by UUID"""
        result = await self.session.execute(
            select(self.model).where(self.model.uuid == uuid)
        )
        return result.scalar_one_or_none()
    
    async def get_all(
        self, 
        offset: int = 0, 
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """Get all entities with pagination"""
        query = select(self.model).offset(offset).limit(limit)
        
        if order_by:
            if hasattr(self.model, order_by):
                query = query.order_by(getattr(self.model, order_by))
        else:
            # Default order by created_at desc if available
            if hasattr(self.model, 'created_at'):
                query = query.order_by(self.model.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, id: int, update_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update entity by ID"""
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        if not update_data:
            return await self.get_by_id(id)
        
        # Add updated_at timestamp if model has it
        if hasattr(self.model, 'updated_at'):
            from datetime import datetime, timezone
            update_data['updated_at'] = datetime.now(timezone.utc)
        
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**update_data)
        )
        await self.session.commit()
        
        return await self.get_by_id(id)
    
    async def delete(self, id: int) -> bool:
        """Delete entity by ID"""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
    
    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities with optional filters"""
        query = select(func.count(self.model.id))
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        result = await self.session.execute(query)
        return result.scalar()
    
    async def exists(self, filters: Dict[str, Any]) -> bool:
        """Check if entity exists with given filters"""
        query = select(self.model.id)
        
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        
        query = query.limit(1)
        result = await self.session.execute(query)
        return result.scalar_one_or_none() is not None