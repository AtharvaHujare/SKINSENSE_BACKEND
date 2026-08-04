"""
SkinSense AI - Database Engine & Connection Module.

Configures the asynchronous SQLAlchemy 2.0 SQLite database engine,
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

# Initialize asynchronous SQLAlchemy 2.0 SQLite database engine
engine: AsyncEngine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=settings.DEBUG,
    future=True,
    connect_args={"check_same_thread": False},
)

# Configures the thread-safe asynchronous session factory
AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def verify_database_connection() -> bool:
    """
    Verifies connectivity to the SQLite database on application startup.
    Executes a lightweight ping query ('SELECT 1') and logs the operational status.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        print("✅ SQLite Database Connected Successfully")
        return True
    except Exception as exc:
        print(f"❌ Database Connection Failed: {exc}", file=sys.stderr)
        return False
