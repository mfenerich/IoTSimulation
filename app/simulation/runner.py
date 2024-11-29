"""
Runner script for the temperature simulation.

This module initializes and runs the simulation for multiple buildings
and rooms concurrently using asyncio.
"""

import asyncio
from app.simulation.simulator import generate_temperature_data

# Define buildings and rooms for the simulation
BUILDINGS_AND_ROOMS = [
    ("B1", "101"),
    ("B1", "102"),
    ("B2", "201"),
]


async def run_simulation():
    """Run the simulation for multiple buildings and rooms concurrently."""
    # Generate tasks for all buildings and rooms
    tasks = [
        generate_temperature_data(building, room)
        for building, room in BUILDINGS_AND_ROOMS
    ]

    # Run all tasks concurrently
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(run_simulation())
