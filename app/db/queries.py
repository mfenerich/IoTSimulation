from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import SQLAlchemyError
from db.models import Temperature
import logging

logger = logging.getLogger("uvicorn")

async def insert_temperature(
    db: AsyncSession,
    building_id: str,
    room_id: str,
    temperature: float,
    timestamp: datetime
) -> None:
    """
    Inserts a temperature record into the database.
    Converts offset-aware datetime to naive before insertion.
    """
    try:
        # Ensure timestamp is naive
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
        logger.info(f"Temperature added: {building_id}, {room_id}, {temperature}, {timestamp}")
    except SQLAlchemyError as e:
        logger.error(f"Database error during insert: {e}")
        await db.rollback()
        raise

async def get_average_temperature(
    db: AsyncSession,
    building_id: str,
    room_id: str,
    start_time: datetime
) -> float:
    """
    Retrieves the average temperature for a building and room since the given time.
    """
    try:
        stmt = select(func.avg(Temperature.temperature)).where(
            Temperature.building_id == building_id,
            Temperature.room_id == room_id,
            Temperature.timestamp >= start_time
        )
        result = await db.execute(stmt)
        avg_temp = result.scalar()
        logger.info(f"Average temperature queried: {avg_temp} for {building_id}, {room_id}")
        return avg_temp
    except SQLAlchemyError as e:
        logger.error(f"Database error during query: {e}")
        raise
