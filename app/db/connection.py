import asyncpg
from fastapi import FastAPI

DATABASE_URL = "postgresql://postgres:password@postgres:5432/temperature_service"

async def connect_to_db():
    return await asyncpg.create_pool(DATABASE_URL)

async def close_db_connection(pool):
    await pool.close()
