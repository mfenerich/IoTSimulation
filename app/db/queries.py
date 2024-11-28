from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import func
from db.models import Temperature
import logging

logger = logging.getLogger("uvicorn")

async def insert_temperature(db: AsyncSession, building_id: str, room_id: str, temperature: float, timestamp):
    # Convert offset-aware datetime to naive datetime
    if timestamp.tzinfo is not None:
        timestamp = timestamp.replace(tzinfo=None)

    new_temp = Temperature(
        building_id=building_id,
        room_id=room_id,
        temperature=temperature,
        timestamp=timestamp
    )
    db.add(new_temp)
    await db.commit()

async def get_average_temperature(db: AsyncSession, building_id: str, room_id: str, start_time):
    stmt = select(func.avg(Temperature.temperature)).where(
        Temperature.building_id == building_id,
        Temperature.room_id == room_id,
        Temperature.timestamp >= start_time
    )
    result = await db.execute(stmt)
    return result.scalar()
