from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from api.v1.temperature import router as temperature_router
from core.config import settings
import logging
from core.logging_config import logger

app = FastAPI()

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
app.include_router(temperature_router, prefix="/v1/temperature", tags=["Temperature"])

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

@app.get("/settings", tags=["Settings"])
async def get_settings():
    return {"app_name": settings.app_name, "debug": settings.debug}