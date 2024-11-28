import asyncio
from simulation.simulator import generate_temperature_data

async def run_simulation():
    """
    Run simulation for multiple buildings and rooms.
    """
    tasks = [
        generate_temperature_data("B1", "101"),
        generate_temperature_data("B1", "102"),
        generate_temperature_data("B2", "201"),
    ]

    # Run all tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(run_simulation())
