from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, root_validator

class TemperatureRequest(BaseModel):
    building_id: str = Field(..., description="ID of the building")
    room_id: str = Field(..., description="ID of the room within the building")
    temperature: float = Field(..., description="Measured temperature in Celsius", ge=-50, le=50)
    timestamp: datetime = Field(..., description="Time of measurement (ISO 8601 format)")

class TemperatureQuery(BaseModel):
    building_id: str = Field(..., min_length=1, description="ID of the building (non-empty)")
    room_id: str = Field(..., min_length=1, description="ID of the room within the building (non-empty)")
    query_datetime: Optional[datetime] = Field(
        None, description="Datetime for querying temperature (optional, defaults to current time)"
    )

    @root_validator(pre=True)
    def validate_fields(cls, values):
        """
        Validate and adjust the query fields if necessary.
        """
        if not values.get("building_id") or not values.get("room_id"):
            raise ValueError("Both building_id and room_id must be provided and non-empty.")
        return values
