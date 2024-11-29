"""
Simulator module for generating and sending temperature data.

This module provides functions to simulate temperature readings for IoT systems,
including retry logic for sending data to the API and configurable intervals.
"""

import asyncio
import datetime
import logging
import random

import pytz
import requests

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


def send_with_retry(url, payload, retries=3, backoff_factor=2):
    """Send data with retry logic for transient failures."""
    for attempt in range(retries):
        try:
            response = requests.post(
                url, json=payload, headers={"Content-Type": "application/json"}
            )
            if response.status_code == 201:
                return True
            logger.error(
                f"Attempt {attempt + 1} failed: {response.status_code}, {response.text}"
            )
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} error: {e}")
        asyncio.run(asyncio.sleep(backoff_factor**attempt))
    return False


async def generate_temperature_data(building_id, room_id):
    """Generate and send temperature data for a specific building and room."""
    while True:
        timestamp = datetime.datetime.now(TIMEZONE)
        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")

        temperature_data = {
            "building_id": building_id,
            "room_id": room_id,
            "temperature": generate_random_temperature(),
            "timestamp": timestamp.isoformat(),
        }

        if send_with_retry(API_URL, temperature_data):
            logger.info(f"Successfully sent data: {temperature_data}")
        else:
            logger.error(f"Failed to send data after retries: {temperature_data}")

        # Wait for the configured interval before sending the next data point
        await asyncio.sleep(settings.data_interval)
