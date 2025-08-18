import os
import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

# Ensure models are imported so metadata is populated
try:
    from api.models import database as models  # noqa: F401
    from api.models import company  # noqa: F401
except Exception as e:
    print(f"[alembic] Warn: could not import models: {e}")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def _to_async_url(url: str) -> str:
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

def get_db_url_async() -> str:
    url = os.getenv("DATABASE_URL", "")
    if not url:
        return "postgresql+asyncpg://vocaliq:vocaliq@localhost:5432/vocaliq"
    # Replace postgres hostname with localhost for local development
    url = url.replace("@postgres:", "@localhost:")
    return _to_async_url(url)

def get_db_url_sync() -> str:
    url = get_db_url_async()
    return url.replace("postgresql+asyncpg://", "postgresql://")

def run_migrations_offline() -> None:
    context.configure(
        url=get_db_url_sync(),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online() -> None:
    connectable = create_async_engine(get_db_url_async(), poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def do_run_migrations(connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
