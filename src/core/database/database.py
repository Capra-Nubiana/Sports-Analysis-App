"""
SQLAlchemy async engine and session management.

Copyright (c) 2026 Philip Kwimba. All rights reserved.
Licensed under AGPLv3 (see LICENSE).
"""

import os
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://localhost/sports_analysis",
)

engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

SessionLocal = async_sessionmaker[AsyncSession](
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session
