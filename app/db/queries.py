from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql.functions import func
from sqlalchemy.exc import SQLAlchemyError
from db.models import Temperature, AvgTemperature
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
        # Ensure timestamp is timezone-aware
        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")
        
        # Convert timestamp to UTC
        timestamp = timestamp.astimezone(timezone.utc)

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
    start_time: Optional[datetime] = None
) -> float:
    """
    Retrieves the average temperature for a building and room from the continuous aggregate view.
    If start_time is not provided, returns the last available average.
    """
    try:
        if start_time is not None:
            # Query the average over the specified time range
            stmt = select(AvgTemperature.avg_temp).where(
                AvgTemperature.building_id == building_id,
                AvgTemperature.room_id == room_id,
                AvgTemperature.bucket >= start_time,
            )
        else:
            # Get the latest avg_temp from the most recent bucket
            stmt = select(AvgTemperature.avg_temp).where(
                AvgTemperature.building_id == building_id,
                AvgTemperature.room_id == room_id,
            ).order_by(AvgTemperature.bucket.desc()).limit(1)

        result = await db.execute(stmt)
        avg_temp = result.scalar()

        logger.info(f"Average temperature queried: {avg_temp} for {building_id}, {room_id}")
        return avg_temp
    except SQLAlchemyError as e:
        logger.error(f"Database error during query: {e}")
        raise