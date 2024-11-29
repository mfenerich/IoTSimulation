"""
Main entry point for the FastAPI IoT Temperature API.

This module initializes the FastAPI application, sets up routes,
handles exceptions, and configures event hooks for startup and shutdown.
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.v1.temperature import router as temperature_router
from app.core.config import settings
from app.core.logging_config import logger
from app.response_models import SettingsResponse

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
    """Log the startup of the FastAPI IoT Simulation Service."""
    logger.info("Starting FastAPI IoT Simulation Service")


@app.on_event("shutdown")
async def shutdown():
    """Log the shutdown of the FastAPI IoT Simulation Service."""
    logger.info("Shutting down FastAPI IoT Simulation Service")


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Check the health of the service.

    Returns:
        JSONResponse: Status and message indicating health.
    """
    return JSONResponse(
        content={"status": "ok", "message": "Service is healthy"}, status_code=200
    )


# Include Temperature Router
app.include_router(
    temperature_router, prefix="/v1/temperature", tags=["Temperature Management"]
)


@app.get(
    "/settings",
    response_model=SettingsResponse,
    summary="Get Application Settings",
    description="Retrieve the application settings such as app name and debug mode.",
    tags=["Settings"],
)
async def get_settings() -> SettingsResponse:
    """
    Retrieve the application settings.

    Returns:
        SettingsResponse: Contains the app name and debug mode status.
    """
    return SettingsResponse(app_name=settings.app_name, debug=settings.debug)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Handle HTTP exceptions by logging and returning a standardized response.

    Args:
        request (Request): The incoming request object.
        exc (HTTPException): The exception being handled.

    Returns:
        JSONResponse: A JSON response with the error details.
    """
    logging.error(f"HTTP Exception: {exc.detail} - Path: {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail, "code": exc.status_code},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handle unexpected exceptions by logging and returning a generic response.

    Args:
        request (Request): The incoming request object.
        exc (Exception): The exception being handled.

    Returns:
        JSONResponse: A JSON response indicating an internal server error.
    """
    logging.error(f"Unexpected error: {exc} - Path: {request.url}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred. Please try again later.",
            "code": 500,
        },
    )
