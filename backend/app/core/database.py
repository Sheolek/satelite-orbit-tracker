from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from typing import AsyncGenerator

from app.core.config import settings

async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo = settings.DEBUG,
    future = True
)

async_session_factory = async_sessionmaker(
    async_engine,
    class_= AsyncSession,
    expire_on_commit = False
)

class Base(DeclarativeBase):
    """Base class for all ORM models.

    All SQLAlchemy ORM models (Satellite, TLE) inherit from this class.
    SQLAlchemy uses this to track table metadata and generate DDL statements.
    The `Base.metadata.create_all()` call in main.py uses this to auto-create
    database tables on application startup.
    """

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            # If the route handler completed without raising, commit all changes
            await session.commit()
        except Exception:
            # If any error occurred, roll back all changes to maintain consistency
            await session.rollback()
            raise
        finally:
            # Always close the session to return the connection to the pool
            await session.close()