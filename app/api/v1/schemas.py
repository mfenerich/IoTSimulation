from pydantic import BaseModel
from datetime import datetime

class TemperatureRequest(BaseModel):
    building_id: str
    room_id: str
    temperature: float
    timestamp: datetime

class TemperatureQuery(BaseModel):
    building_id: str
    room_id: str