from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

DATABASE_URL = settings.database_url

engine = create_async_engine(DATABASE_URL, echo=True)

async_session_factory = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Dependency to provide database session
async def get_db():
    async with async_session_factory() as session:
        yield session
