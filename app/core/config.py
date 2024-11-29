"""
This module defines the application configuration using Pydantic's BaseSettings.

The configuration is loaded from environment variables and supports default values.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings configuration.

    Attributes:
        app_name (str): The name of the application.
        debug (bool): Flag to enable or disable debug mode.
        database_url (str): Database connection string.
        alignment_interval (int): Time alignment interval in minutes.
        api_url (str): Base URL for the API.
        timezone (str): Default timezone for the application.
        data_interval (int): Interval between data points in seconds.
    """

    app_name: str = "FastAPI IoT Simulation"
    debug: bool = True
    database_url: str
    alignment_interval: int = 4
    api_url: str = "http://localhost:8000/v1/temperature/"
    timezone: str = "Europe/Zurich"
    data_interval: int = 5  # Interval between data points in seconds

    class Config:
        """
        Configuration class for Pydantic BaseSettings.

        Specifies the environment file from which settings should be loaded.
        """

        env_file = ".env"


settings = Settings()
