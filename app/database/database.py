"""
SkinSense AI - Database Engine & Connection Module.

Initializes the SQLAlchemy async engine and async session factory.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# Database connection configuration defaults
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/skinsense"

# Initialize asynchronous engine instance
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Async session maker factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)
