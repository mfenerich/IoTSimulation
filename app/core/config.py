from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "FastAPI IoT Simulation"
    debug: bool = True
    database_url: str
    alignment_interval: int = 4

    class Config:
        env_file = ".env"

settings = Settings()
