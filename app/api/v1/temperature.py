from api.v1.schemas import TemperatureRequest, TemperatureQuery
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.connection import get_db
from db.queries import insert_temperature, get_average_temperature
from datetime import datetime, timedelta
from fastapi import HTTPException

router = APIRouter()

@router.post("/")
async def add_temperature(
    temperature_data: TemperatureRequest,
    db: AsyncSession = Depends(get_db)
):
    await insert_temperature(
        db,
        building_id=temperature_data.building_id,
        room_id=temperature_data.room_id,
        temperature=temperature_data.temperature,
        timestamp=temperature_data.timestamp,
    )
    return {"message": "Temperature data added"}

@router.get("/average")
async def fetch_average_temperature(
    query: TemperatureQuery = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        start_time = datetime.utcnow() - timedelta(minutes=15)
        avg_temp = await get_average_temperature(db, query.building_id, query.room_id, start_time)
        if avg_temp is None:
            return {"message": "No data found"}
        return {"average_temperature": avg_temp}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
