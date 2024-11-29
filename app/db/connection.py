from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from core.config import settings

# Create the database engine
DATABASE_URL = settings.database_url
engine = create_async_engine(DATABASE_URL, echo=True)

# Create an async session factory
async_session_factory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Dependency to provide database session
async def get_db() -> AsyncSession:
    async with async_session_factory() as session:
        yield session
