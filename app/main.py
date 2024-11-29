from fastapi import FastAPI, HTTPException, Request, APIRouter
from fastapi.responses import JSONResponse
from api.v1.temperature import router as temperature_router
from core.config import settings
import logging
from core.logging_config import logger
from response_models import SettingsResponse
from core.config import settings

app = FastAPI(
    title="IoT Temperature API",
    description="""
    This API allows clients to manage temperature data for IoT systems.

    Features:
    - Add temperature data for buildings and rooms.
    - Fetch average temperature data for a specified time range.
    """,
    version="1.0.0",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "API Support",
        "url": "http://feneri.ch",
        "email": "marcel@feneri.ch",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

@app.on_event("startup")
async def startup():
    logger.info("Starting FastAPI IoT Simulation Service")

@app.on_event("shutdown")
async def shutdown():
    logger.info("Shutting down FastAPI IoT Simulation Service")

# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health Check

    This endpoint verifies the service's health status.
    Returns:
        - status (str): "ok" if healthy
        - message (str): Detailed message
    """
    return JSONResponse(content={"status": "ok", "message": "Service is healthy"}, status_code=200)

# Include Temperature Router
app.include_router(temperature_router, prefix="/v1/temperature", tags=["Temperature Management"])

@app.get(
    "/settings",
    response_model=SettingsResponse,
    summary="Get Application Settings",
    description="Retrieve the application settings such as app name and debug mode.",
    tags=["Settings"]
)
async def get_settings() -> SettingsResponse:
    return SettingsResponse(app_name=settings.app_name, debug=settings.debug)

# Custom exception handler for HTTP exceptions
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logging.error(f"HTTP Exception: {exc.detail} - Path: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.status_code},
    )

# Custom exception handler for generic errors
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logging.error(f"Unexpected error: {exc} - Path: {request.url}")
    return JSONResponse(
        status_code=500,
        content={"error": "An unexpected error occurred. Please try again later.", "code": 500},
    )
