"""
Tests for the simulator module.

This module contains unit tests for the core functionalities of
`app.simulation.simulator`, including temperature generation, data
sending with retry logic, and proper handling of configurations like
timezones and API calls.
"""

import datetime
from unittest.mock import AsyncMock, patch

import pytest

from app.simulation.simulator import (
    generate_random_temperature,
    generate_temperature_data,
    send_with_retry,
)


def test_generate_random_temperature():
    """Test the generate_random_temperature function."""
    from app.simulation.simulator import generate_random_temperature

    min_temp = -20
    max_temp = 40
    for _ in range(100):
        temp = generate_random_temperature(min_temp, max_temp)
        assert min_temp <= temp <= max_temp


@pytest.mark.asyncio
async def test_send_with_retry_retries(mocker):
    """Test send_with_retry retries on failure."""
    mock_post = mocker.patch(
        "aiohttp.ClientSession.post", side_effect=Exception("Network error")
    )

    from app.simulation.simulator import send_with_retry

    result = await send_with_retry(
        "http://dummy-url.com", {"data": "test"}, retries=3, backoff_factor=0.1
    )

    assert not result  # Function should return False after max retries
    assert mock_post.call_count == 3  # Ensure it retried 3 times


@pytest.mark.asyncio
async def test_send_with_retry_backoff(mocker):
    """Test send_with_retry backs off correctly between retries."""
    mock_post = mocker.patch(
        "aiohttp.ClientSession.post", side_effect=Exception("Network error")
    )
    sleep_mock = mocker.patch(
        "app.simulation.simulator.asyncio.sleep", new_callable=AsyncMock
    )

    retries = 3
    backoff_factor = 0.1

    await send_with_retry(
        "http://dummy-url.com",
        {"data": "test"},
        retries=retries,
        backoff_factor=backoff_factor,
    )

    expected_delays = [backoff_factor**attempt for attempt in range(retries)]
    actual_delays = [call.args[0] for call in sleep_mock.call_args_list]

    assert actual_delays == expected_delays
    assert mock_post.call_count == retries


@pytest.mark.asyncio
async def test_generate_temperature_data_valid(mocker):
    """Test generate_temperature_data sends correct data."""
    mock_send_with_retry = mocker.patch(
        "app.simulation.simulator.send_with_retry", new_callable=AsyncMock
    )
    mock_send_with_retry.return_value = True

    # Mock settings to control data_interval
    with patch("app.simulation.simulator.settings") as mock_settings:
        mock_settings.data_interval = 0.01
        mock_settings.api_url = "http://dummy-url.com"
        mock_settings.timezone = "UTC"

        await generate_temperature_data("B1", "101", max_iterations=1)

    assert mock_send_with_retry.call_count == 1
    sent_data = mock_send_with_retry.call_args[0][1]
    assert sent_data["building_id"] == "B1"
    assert sent_data["room_id"] == "101"
    assert isinstance(sent_data["temperature"], float)
    assert "timestamp" in sent_data


def test_generate_random_temperature_defaults():
    """Test generate_random_temperature with default min and max temperatures."""
    temperatures = [generate_random_temperature() for _ in range(100)]
    assert all(-50 <= temp <= 50 for temp in temperatures)


@pytest.mark.asyncio
async def test_generate_temperature_data_timestamp_tz_aware(mocker):
    """Test that the timestamp is timezone-aware."""
    mock_send_with_retry = mocker.patch(
        "app.simulation.simulator.send_with_retry", new_callable=AsyncMock
    )
    mock_send_with_retry.return_value = True

    # Mock settings to control data_interval
    with patch("app.simulation.simulator.settings") as mock_settings:
        mock_settings.data_interval = 0.01
        mock_settings.api_url = "http://dummy-url.com"
        mock_settings.timezone = "UTC"

        await generate_temperature_data("B1", "101", max_iterations=1)

    sent_data = mock_send_with_retry.call_args[0][1]
    timestamp = datetime.datetime.fromisoformat(sent_data["timestamp"])
    assert timestamp.tzinfo is not None


@pytest.mark.asyncio
async def test_generate_temperature_data_max_iterations(mocker):
    """Test that generate_temperature_data stops after max_iterations."""
    mock_send_with_retry = mocker.patch(
        "app.simulation.simulator.send_with_retry", new_callable=AsyncMock
    )
    mock_send_with_retry.return_value = True

    with patch("app.simulation.simulator.settings") as mock_settings:
        mock_settings.data_interval = 0.01
        await generate_temperature_data("B1", "101", max_iterations=3)

    assert mock_send_with_retry.call_count == 3


@pytest.mark.asyncio
async def test_send_with_retry_handles_exception(mocker):
    """Test send_with_retry handles exceptions and retries."""
    mock_post = mocker.patch(
        "aiohttp.ClientSession.post", side_effect=Exception("Network error")
    )

    # Mock asyncio.sleep to avoid delays
    sleep_mock = mocker.patch(
        "app.simulation.simulator.asyncio.sleep", new_callable=AsyncMock
    )

    result = await send_with_retry(
        "http://dummy-url.com", {"data": "test"}, retries=2, backoff_factor=0
    )

    assert not result
    assert mock_post.call_count == 2
    assert sleep_mock.call_count == 2  # Should sleep between retries


@pytest.mark.asyncio
async def test_generate_temperature_data_logs_error(mocker):
    """Test that generate_temperature_data logs an error when sending fails."""
    mock_send_with_retry = mocker.patch(
        "app.simulation.simulator.send_with_retry", new_callable=AsyncMock
    )
    mock_send_with_retry.return_value = False  # Simulate send failure

    mock_logger_error = mocker.patch("app.simulation.simulator.logger.error")

    with patch("app.simulation.simulator.settings") as mock_settings:
        mock_settings.data_interval = 0.01
        await generate_temperature_data("B1", "101", max_iterations=1)

    assert mock_send_with_retry.call_count == 1
    mock_logger_error.assert_called_with(
        f"Failed to send data after retries: {mock_send_with_retry.call_args[0][1]}"
    )
