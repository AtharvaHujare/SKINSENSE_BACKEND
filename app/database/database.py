"""
SkinSense AI - Database Engine & Connection Module.

Configures the asynchronous SQLAlchemy 2.0 database engine, connection pool,
session factory, and health verification utilities.
"""

import sys
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from app.config import settings

# Initialize asynchronous SQLAlchemy 2.0 database engine
# Uses postgresql+asyncpg protocol built dynamically in Settings property
engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,  # Test connection prior to usage to avoid stale handles
    pool_size=settings.DB_POOL_SIZE,  # Maximum number of active pool connections
    max_overflow=settings.DB_MAX_OVERFLOW,  # Temporary connections beyond pool_size
    pool_timeout=settings.DB_POOL_TIMEOUT,  # Timeout seconds waiting for connection
)

# Configures the thread-safe asynchronous session factory
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents attribute expiration after commit for async usage
    autoflush=False,         # Prevents automatic flush prior to query execution
    autocommit=False,        # Enforces explicit transaction commits
)


async def verify_database_connection() -> bool:
    """
    Verifies connectivity to the PostgreSQL database on application startup.
    Executes a lightweight ping query ('SELECT 1') and logs the operational status.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        print("✅ Database Connected Successfully")
        return True
    except Exception as exc:
        print(f"❌ Database Connection Failed: {exc}", file=sys.stderr)
        return False
