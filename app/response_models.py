"""
Pydantic response models for the FastAPI application.

These models define the structure of API responses for various endpoints.
"""

from pydantic import BaseModel
from typing import Optional


class AddTemperatureResponse(BaseModel):
    """
    Response model for adding temperature data.

    Attributes:
        message (str): Success message indicating the data was added.
    """

    message: str


class AverageTemperatureResponse(BaseModel):
    """
    Response model for fetching average temperature data.

    Attributes:
        average_temperature (Optional[float]):
            The average temperature for the specified range.
        message (Optional[str]): Optional message, usually if no data is found.
    """

    average_temperature: Optional[float] = None
    message: Optional[str] = None


class SettingsResponse(BaseModel):
    """
    Response model for retrieving application settings.

    Attributes:
        app_name (str): The name of the application.
        debug (bool): Indicates if the application is in debug mode.
    """

    app_name: str
    debug: bool
