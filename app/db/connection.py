"""
Database connection and session management for the FastAPI application.

This module configures the database engine and provides a dependency
for retrieving an asynchronous database session.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Create the database engine
DATABASE_URL = settings.database_url
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session factory
async_session_factory = sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncSession:
    """
    Provide a database session for FastAPI routes.

    This function yields an asynchronous SQLAlchemy session, ensuring that
    the session is properly closed after use.

    Yields:
        AsyncSession: The database session to be used within a route.
    """
    async with async_session_factory() as session:
        yield session
