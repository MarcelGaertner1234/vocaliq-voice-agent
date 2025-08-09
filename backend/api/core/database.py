"""
VocalIQ Database Configuration
SQLModel + SQLAlchemy Database Setup mit PostgreSQL
"""
import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import event, text
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from api.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)

# Database Engine
engine = None
async_session_maker = None


def get_database_url() -> str:
    """Get database URL from settings"""
    if settings.DATABASE_URL:
        # Convert postgres:// to postgresql+asyncpg://
        url = settings.DATABASE_URL
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        return url
    
    # Build URL from components
    return (
        f"postgresql+asyncpg://{settings.DATABASE_USER}:{settings.DATABASE_PASSWORD}"
        f"@{settings.DATABASE_HOST}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}"
    )


def create_database_engine():
    """Create database engine"""
    global engine, async_session_maker
    
    database_url = get_database_url()
    logger.info(f"🗄️ Connecting to database: {database_url.split('@')[1] if '@' in database_url else 'unknown'}")
    
    # Engine configuration
    engine_kwargs = {
        "echo": settings.DEBUG and settings.DATABASE_ECHO,
        "pool_pre_ping": True,
        "pool_recycle": 3600,  # 1 hour
        "connect_args": {
            "server_settings": {
                "application_name": f"VocalIQ-API-{settings.ENVIRONMENT}",
            },
            "command_timeout": 30,
        }
    }
    
    # For testing, use NullPool to avoid connection issues
    if settings.ENVIRONMENT == "test":
        engine_kwargs["poolclass"] = NullPool
    else:
        engine_kwargs.update({
            "pool_size": settings.DATABASE_POOL_SIZE,
            "max_overflow": settings.DATABASE_MAX_OVERFLOW,
            "pool_timeout": 30,
        })
    
    engine = create_async_engine(database_url, **engine_kwargs)
    
    # Session maker
    async_session_maker = async_sessionmaker(
        engine, 
        class_=AsyncSession, 
        expire_on_commit=False
    )
    
    # Add event listeners
    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        """Set SQLite pragma for foreign key support (if using SQLite)"""
        if "sqlite" in str(engine.url):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        """Log slow queries in debug mode"""
        if settings.DEBUG:
            context._query_start_time = logger.info(f"🔍 Executing SQL: {statement[:100]}...")
    
    return engine


async def create_tables():
    """Create all database tables"""
    if not engine:
        create_database_engine()
    
    try:
        logger.info("📋 Creating database tables...")
        
        # Import all models to ensure they're registered
        from api.models.database import (
            Organization, User, PhoneNumber, CallLog, 
            Conversation, CallAnalytics, APIKey, SystemConfig
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {str(e)}")
        raise


async def drop_tables():
    """Drop all database tables (for testing/development)"""
    if not engine:
        create_database_engine()
    
    try:
        logger.warning("🗑️ Dropping all database tables...")
        
        from api.models.database import (
            Organization, User, PhoneNumber, CallLog, 
            Conversation, CallAnalytics, APIKey, SystemConfig
        )
        
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        
        logger.info("✅ Database tables dropped successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {str(e)}")
        raise


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get database session
    FastAPI Dependency
    """
    if not async_session_maker:
        create_database_engine()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_session_context() -> AsyncSession:
    """
    Get database session context manager
    For use outside of FastAPI (e.g., background tasks)
    """
    if not async_session_maker:
        create_database_engine()
    
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def health_check() -> dict:
    """Database health check"""
    if not engine:
        return {
            "status": "not_initialized",
            "error": "Database engine not initialized"
        }
    
    try:
        async with engine.begin() as conn:
            # Simple query to test connection
            result = await conn.execute(text("SELECT 1 as test"))
            test_value = result.scalar()
            
            if test_value == 1:
                return {
                    "status": "healthy",
                    "database_url": str(engine.url).split('@')[1] if '@' in str(engine.url) else "unknown",
                    "pool_size": getattr(engine.pool, 'size', 'unknown'),
                    "checked_out_connections": getattr(engine.pool, 'checkedout', 'unknown'),
                }
            else:
                return {
                    "status": "error", 
                    "error": "Unexpected query result"
                }
                
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


async def close_database():
    """Close database connections"""
    global engine, async_session_maker
    
    if engine:
        logger.info("🔒 Closing database connections...")
        await engine.dispose()
        engine = None
        async_session_maker = None
        logger.info("✅ Database connections closed")


# Database utilities
async def execute_sql(query: str, params: Optional[dict] = None) -> any:
    """Execute raw SQL query"""
    async with get_session_context() as session:
        result = await session.execute(text(query), params or {})
        await session.commit()
        return result


async def get_table_counts() -> dict:
    """Get row counts for all tables"""
    counts = {}
    
    try:
        async with get_session_context() as session:
            tables = [
                "organizations", "users", "phone_numbers", "call_logs",
                "conversations", "call_analytics", "api_keys", "system_config"
            ]
            
            for table in tables:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                counts[table] = result.scalar()
                
    except Exception as e:
        logger.error(f"Error getting table counts: {str(e)}")
        counts["error"] = str(e)
    
    return counts


# Migration helpers
async def check_table_exists(table_name: str) -> bool:
    """Check if a table exists"""
    try:
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = :table_name
                )
                """),
                {"table_name": table_name}
            )
            return result.scalar()
    except Exception:
        return False


async def create_indexes():
    """Create additional database indexes for performance"""
    indexes = [
        "CREATE INDEX IF NOT EXISTS idx_call_logs_created_at ON call_logs(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_call_logs_status ON call_logs(status)",
        "CREATE INDEX IF NOT EXISTS idx_call_logs_direction ON call_logs(direction)",
        "CREATE INDEX IF NOT EXISTS idx_call_logs_from_number ON call_logs(from_number)",
        "CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON conversations(session_id)",
        "CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at DESC)",
        "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
        "CREATE INDEX IF NOT EXISTS idx_users_status ON users(status)",
        "CREATE INDEX IF NOT EXISTS idx_organizations_slug ON organizations(slug)",
        "CREATE INDEX IF NOT EXISTS idx_phone_numbers_number ON phone_numbers(number)",
        "CREATE INDEX IF NOT EXISTS idx_call_analytics_date ON call_analytics(date DESC)",
        "CREATE INDEX IF NOT EXISTS idx_call_analytics_org_date ON call_analytics(organization_id, date)",
    ]
    
    try:
        logger.info("📊 Creating database indexes...")
        async with engine.begin() as conn:
            for index_sql in indexes:
                try:
                    await conn.execute(text(index_sql))
                    logger.debug(f"✅ Created index: {index_sql.split(' ON ')[1].split('(')[0]}")
                except Exception as e:
                    logger.warning(f"Index creation warning: {str(e)}")
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {str(e)}")
        raise


# Initialize database on import in production
if settings.ENVIRONMENT != "test":
    create_database_engine()