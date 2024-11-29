"""
This module defines the API endpoints for managing temperature data.

Endpoints:
- `add_temperature`: Save temperature data for a building and room.
- `fetch_average_temperature`: Get the average temperature over a specified time period.
"""

import logging
import traceback
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.schemas import TemperatureQuery, TemperatureRequest
from app.core.dependencies import get_db
from app.core.utils import align_time_to_interval
from app.db.queries import get_average_temperature, insert_temperature
from app.response_models import AddTemperatureResponse, AverageTemperatureResponse

logger = logging.getLogger("uvicorn")

# Router setup
router = APIRouter()

# Module-level defaults
default_db_dependency = Depends(get_db)
default_query_dependency = Depends()


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
    - `temperature`: The temperature reading
        (must be between -50 and 50 degrees Celsius).
    - `timestamp`: ISO8601 formatted timestamp of the temperature reading.

    Returns:
    - A success message when the data is saved successfully.
    """,
)
async def add_temperature(
    temperature_data: TemperatureRequest, db: AsyncSession = default_db_dependency
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
        logger.info(
            f"Temperature data added for Building ID: {temperature_data.building_id}, "
            f"Room ID: {temperature_data.room_id}"
        )
        return {"message": "Temperature data added"}
    except SQLAlchemyError as e:
        logger.error(f"Database error while adding temperature: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        incident_id = str(uuid.uuid4())
        logger.error(f"Incident {incident_id}: Unexpected error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred. Reference ID: {incident_id}",
        )


@router.get(
    "/average",
    response_model=AverageTemperatureResponse,
    summary="Get Average Temperature",
    description="""
    Fetch the average temperature over a specified time period for a building and room.

    Query Parameters:
    - `building_id`: The ID of the building.
    - `room_id`: The ID of the room.
    - `query_datetime`: Optional. The datetime for the query
        (defaults to the current time).

    Returns:
    - The average temperature for the specified time period,
        or a message if no data is found.
    """,
)
async def fetch_average_temperature(
    query: TemperatureQuery = default_query_dependency,
    db: AsyncSession = default_db_dependency,
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
            logger.info(
                f"No temperature data found for Building ID: {query.building_id}, "
                f"Room ID: {query.room_id}"
            )
            return {"message": "No data found"}

        logger.info(
            f"Average temperature for Building ID: {query.building_id}, "
            f"Room ID: {query.room_id}, Start Time: {start_time} is {avg_temp}"
        )
        return {"average_temperature": avg_temp}
    except SQLAlchemyError as e:
        logger.error(f"Database error while fetching average temperature: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred.")
    except Exception as e:
        incident_id = str(uuid.uuid4())
        logger.error(f"Incident {incident_id}: Unexpected error: {e}")
        logger.error(traceback.format_exc())  # Log the full stack trace
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred. Reference ID: {incident_id}",
        )
