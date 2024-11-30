"""
Simulator module for generating and sending temperature data.

This module provides functions to simulate temperature readings for IoT systems,
including retry logic for sending data to the API and configurable intervals.
"""

import asyncio
import datetime
import logging
import random

import aiohttp
import pytz

from app.core.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TemperatureSimulator")

# Load configuration from settings
API_URL = settings.api_url
try:
    TIMEZONE = pytz.timezone(settings.timezone)
except pytz.UnknownTimeZoneError:
    logger.warning(
        f"Invalid timezone in settings: {settings.timezone}. Defaulting to UTC."
    )
    TIMEZONE = pytz.UTC


def generate_random_temperature(min_temp=-50, max_temp=50):
    """Generate a random temperature within the given range."""
    return round(random.uniform(min_temp, max_temp), 2)


async def send_with_retry(url, payload, retries=3, backoff_factor=2):
    """Send data with retry logic for transient failures."""
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=payload, headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 201:
                        return True
                    logger.error(
                        f"Attempt {attempt + 1} failed: {response.status}, "
                        f"{await response.text()}"
                    )

        except Exception as e:
            logger.error(f"Attempt {attempt + 1} error: {e}")

        # Wait before retrying
        await asyncio.sleep(backoff_factor**attempt)
    return False


async def generate_temperature_data(building_id, room_id, max_iterations=None):
    """Generate and send temperature data for a specific building and room."""
    iteration = 0
    while max_iterations is None or iteration < max_iterations:
        timestamp = datetime.datetime.now(TIMEZONE)
        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")

        temperature_data = {
            "building_id": building_id,
            "room_id": room_id,
            "temperature": generate_random_temperature(),
            "timestamp": timestamp.isoformat(),
        }

        if await send_with_retry(API_URL, temperature_data):
            logger.info(f"Successfully sent data: {temperature_data}")
        else:
            logger.error(f"Failed to send data after retries: {temperature_data}")

        iteration += 1
        await asyncio.sleep(settings.data_interval)
