from pydantic import BaseModel
from typing import Optional

class AddTemperatureResponse(BaseModel):
    message: str

class AverageTemperatureResponse(BaseModel):
    average_temperature: Optional[float] = None
    message: Optional[str] = None

class SettingsResponse(BaseModel):
    app_name: str
    debug: bool
