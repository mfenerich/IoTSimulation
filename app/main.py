from fastapi import FastAPI
from api.v1.temperature import router as temperature_router

app = FastAPI()

@app.on_event("startup")
async def startup():
    pass  # Add any necessary startup logic

@app.on_event("shutdown")
async def shutdown():
    pass  # Add any necessary shutdown logic

app.include_router(temperature_router, prefix="/v1/temperature", tags=["Temperature"])
