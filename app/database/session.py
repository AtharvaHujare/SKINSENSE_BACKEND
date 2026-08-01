"""
SkinSense AI - Database Session Dependency Provider.

Provides an asynchronous database session generator for request handling.
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.database import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency generator yielding an AsyncSession per HTTP request scope.
    Guarantees clean transaction rollback on error and proper session cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
