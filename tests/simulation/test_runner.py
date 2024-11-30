"""
Tests for the runner module.

This module contains tests for the functions and workflows in
`app.simulation.runner`, including integration tests for the
simulation process and retry logic.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, patch

import pytest

from app.simulation.runner import BUILDINGS_AND_ROOMS, run_simulation
from app.simulation.simulator import generate_temperature_data


@pytest.mark.asyncio
async def test_generate_temperature_data(mocker):
    """Test the generate_temperature_data function."""
    mock_send_with_retry = mocker.patch(
        "app.simulation.simulator.send_with_retry", new_callable=AsyncMock
    )
    mock_send_with_retry.return_value = True

    # Mock asyncio.sleep to avoid delays
    with patch(
        "app.simulation.simulator.asyncio.sleep", new_callable=AsyncMock
    ) as mock_sleep:
        # Run the simulation for 2 iterations
        await generate_temperature_data("B1", "101", max_iterations=2)

    # Ensure send_with_retry is called twice
    assert mock_send_with_retry.call_count == 2
    # Ensure asyncio.sleep was called twice
    assert mock_sleep.call_count == 2


@pytest.mark.asyncio
async def test_run_simulation_with_timeout(mocker):
    """Test the run_simulation function with a controlled timeout."""
    # Mock the generate_temperature_data function
    mock_generate_temperature_data = mocker.patch(
        "app.simulation.runner.generate_temperature_data",
        new_callable=AsyncMock,
    )

    async def mock_temperature_data(*args, **kwargs):
        """Simulate limited iterations."""
        for _ in range(2):  # Simulate two iterations
            await asyncio.sleep(0.1)

    mock_generate_temperature_data.side_effect = mock_temperature_data

    # Run the simulation with a timeout
    try:
        await asyncio.wait_for(
            run_simulation(), timeout=1
        )  # Allow 1 second for the test
    except asyncio.TimeoutError:
        pass  # Expected since the simulation runs indefinitely

    # Ensure generate_temperature_data was called for each building-room pair
    assert mock_generate_temperature_data.call_count == len(BUILDINGS_AND_ROOMS)


@pytest.mark.asyncio
async def test_send_with_retry_error_handling(mocker, caplog):
    """Test the retry logic and logging in send_with_retry."""
    mock_post = mocker.patch(
        "aiohttp.ClientSession.post", side_effect=Exception("Network error")
    )

    from app.simulation.simulator import send_with_retry

    with caplog.at_level(logging.ERROR):
        result = await send_with_retry(
            "http://dummy-url.com", {"data": "test"}, retries=3, backoff_factor=0.1
        )

    # Ensure retries are made
    assert mock_post.call_count == 3

    # Ensure proper logging
    assert "Attempt 1 error: Network error" in caplog.text
    assert "Attempt 2 error: Network error" in caplog.text
    assert "Attempt 3 error: Network error" in caplog.text

    # Ensure the function returns False after max retries
    assert not result
