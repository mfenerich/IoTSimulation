from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.v1.temperature import router as temperature_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    pass  # Add any necessary startup logic

@app.on_event("shutdown")
async def shutdown():
    pass  # Add any necessary shutdown logic

# Health Check Endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return JSONResponse(content={"status": "ok", "message": "Service is healthy"}, status_code=200)

# Include Temperature Router
app.include_router(temperature_router, prefix="/v1/temperature", tags=["Temperature"])

