from api.v1.schemas import TemperatureRequest, TemperatureQuery
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from db.queries import insert_temperature, get_average_temperature
from datetime import datetime
from core.dependencies import get_db
from core.utils import align_time_to_interval
from response_models import AddTemperatureResponse, AverageTemperatureResponse
import logging
import uuid

logger = logging.getLogger("uvicorn")

# Router setup
router = APIRouter()

@router.post(
    "/",
    response_model=AddTemperatureResponse,
    status_code=201,
    summary="Add Temperature Data",
    description="""
    Save temperature data for a specific building and room.

    This endpoint accepts the following fields:
    - `building_id`: The ID of the building.
    - `room_id`: The ID of the room.
    - `temperature`: The temperature reading (must be between -50 and 50 degrees Celsius).
    - `timestamp`: ISO8601 formatted timestamp of the temperature reading.

    Returns:
    - A success message when the data is saved successfully.
    """,
)
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


@router.get(
    "/average",
    response_model=AverageTemperatureResponse,
    summary="Get Average Temperature",
    description="""
    Fetch the average temperature over a specified time period for a building and room.

    Query Parameters:
    - `building_id`: The ID of the building.
    - `room_id`: The ID of the room.
    - `query_datetime`: Optional. The datetime for the query (defaults to the current time).

    Returns:
    - The average temperature for the specified time period, or a message if no data is found.
    """,
)
async def fetch_average_temperature(
    query: TemperatureQuery = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch the average temperature for the last X minutes.

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
