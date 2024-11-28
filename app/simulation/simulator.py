import asyncio
import random
import datetime
import os
import pytz  # For timezone handling
import requests

# Get API URL from environment variables
API_URL = os.getenv("API_URL", "http://localhost:8000/v1/temperature/")

# Define the desired timezone
TIMEZONE = pytz.timezone("Europe/Zurich")

async def generate_temperature_data(building_id, room_id):
    """
    Generate and send temperature data for a specific building and room.
    """
    while True:
        # Generate a timezone-aware timestamp
        timestamp = datetime.datetime.now(TIMEZONE)  # Get current time in the specified timezone
        if timestamp.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware.")  # Ensure it's timezone-aware

        # Create the temperature data payload
        temperature_data = {
            "building_id": building_id,
            "room_id": room_id,
            "temperature": round(random.uniform(15, 30), 2),  # Random temperature between 15 and 30
            "timestamp": timestamp.isoformat(),  # Convert timestamp to ISO8601 format
        }

        try:
            # Send POST request to the API
            response = requests.post(API_URL, json=temperature_data, headers={"Content-Type": "application/json"})
            if response.status_code == 200:
                print(f"Successfully sent data: {temperature_data}")
            else:
                print(f"Failed to send data: {response.status_code}, {response.text}")
        except Exception as e:
            print(f"Error sending data: {e}")

        # Wait for 5 seconds before sending the next data point
        await asyncio.sleep(5)
