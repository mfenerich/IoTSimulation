from api.v1.schemas import TemperatureRequest, TemperatureQuery
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from db.queries import insert_temperature, get_average_temperature
from datetime import datetime
from core.dependencies import get_db
from core.utils import align_time_to_interval
import logging
import uuid

logger = logging.getLogger("uvicorn")

router = APIRouter(
    tags=["Temperature Management"]
)

@router.post("/", response_model=dict, status_code=201, summary="Add Temperature Data")
async def add_temperature(
    temperature_data: TemperatureRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Save temperature data for a specific building and room.

    Args:
        temperature_data (TemperatureRequest): Temperature details.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: Success message.
    """
    try:
        await insert_temperature(
            db,
            building_id=temperature_data.building_id,
            room_id=temperature_data.room_id,
            temperature=temperature_data.temperature,
            timestamp=temperature_data.timestamp,
        )
        logger.info(f"Temperature data added for Building ID: {temperature_data.building_id}, Room ID: {temperature_data.room_id}")
        return {"message": "Temperature data added"}
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding temperature: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        incident_id = str(uuid.uuid4())
        logger.error(f"Incident {incident_id}: Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. Reference ID: {incident_id}")


@router.get("/average", summary="Get Average Temperature", description="Fetch the 15-minute average temperature for a building and room.")
async def fetch_average_temperature(
    query: TemperatureQuery = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch the average temperature for the last 15 minutes.

    Args:
        query (TemperatureQuery): Query parameters.
        db (AsyncSession): Database session dependency.

    Returns:
        dict: Average temperature or message if no data found.
    """
    try:
        now = datetime.now()
        start_time = align_time_to_interval(now)

        if query.query_datetime:
            start_time = query.query_datetime

        avg_temp = await get_average_temperature(
            db, query.building_id, query.room_id, start_time
        )
        if avg_temp is None:
            logger.info(f"No temperature data found for Building ID: {query.building_id}, Room ID: {query.room_id}")
            return {"message": "No data found"}

        logger.info(f"Average temperature for Building ID: {query.building_id}, Room ID: {query.room_id}, Start Time: {start_time} is {avg_temp}")
        return {"average_temperature": avg_temp}
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching average temperature: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        incident_id = str(uuid.uuid4())
        logger.error(f"Incident {incident_id}: Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred. Reference ID: {incident_id}")
