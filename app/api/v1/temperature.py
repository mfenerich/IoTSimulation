from api.v1.schemas import TemperatureRequest, TemperatureQuery
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.queries import insert_temperature, get_average_temperature
from datetime import datetime, timedelta
import logging
from core.dependencies import get_dependencies


logger = logging.getLogger("uvicorn")

router = APIRouter()

@router.post("/")
async def add_temperature(
    temperature_data: TemperatureRequest,
    db: AsyncSession = Depends(get_dependencies)
):
    """
    API endpoint to add temperature data.
    """
    try:
        await insert_temperature(
            db,
            building_id=temperature_data.building_id,
            room_id=temperature_data.room_id,
            temperature=temperature_data.temperature,
            timestamp=temperature_data.timestamp,
        )
        logger.info("Temperature data successfully added.")
        return {"message": "Temperature data added"}
    except Exception as e:
        logger.error(f"Error adding temperature data: {e}")
        raise HTTPException(status_code=500, detail="Failed to add temperature data.")

@router.get("/average", summary="Get Average Temperature", description="Fetch the 15-minute average temperature for a building and room.")
async def fetch_average_temperature(
    query: TemperatureQuery = Depends(),
    db: AsyncSession = Depends(get_dependencies)
):
    """
    API endpoint to fetch the average temperature for the last 15 minutes.
    """
    try:
        start_time = datetime.utcnow() - timedelta(minutes=15)
        avg_temp = await get_average_temperature(
            db,
            query.building_id,
            query.room_id,
            start_time
        )
        if avg_temp is None:
            logger.info("No temperature data found for the query.")
            return {"message": "No data found"}
        logger.info(f"Average temperature: {avg_temp}")
        return {"average_temperature": avg_temp}
    except Exception as e:
        logger.error(f"Error fetching average temperature: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch average temperature.")
