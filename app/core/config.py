from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI IoT Simulation"
    debug: bool = True
    database_url: str
    alignment_interval: int = 4
    api_url: str = "http://localhost:8000/v1/temperature/"
    timezone: str = "Europe/Zurich"
    data_interval: int = 5  # Interval between data points in seconds

    class Config:
        env_file = ".env"

settings = Settings()
