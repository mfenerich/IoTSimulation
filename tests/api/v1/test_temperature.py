"""
Tests for the temperature-related API endpoints.

Includes tests for adding temperature data and fetching average temperature data.
"""

import asyncio
import time
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from httpx import ASGITransport, AsyncClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.main import app


@pytest.fixture
def client():
    """Fixture to provide a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def valid_mock_data():
    """Fixture to provide valid mock data for tests."""
    return {
        "building_id": "1",
        "room_id": "101",
        "temperature": 22.5,
        "timestamp": "2024-01-01T12:00:00",
    }


class TestAddTemperatureEndpoint:
    """
    Test cases for the `/v1/temperature` endpoint.

    Includes tests for success, validation errors, and edge cases.
    """

    @patch("app.api.v1.temperature.insert_temperature")
    def test_add_temperature_success(self, mock_insert, client, valid_mock_data):
        """
        Test the `add_temperature` endpoint with valid data.

        Ensures:
        - HTTP status code is 201.
        - A success message is returned.
        """
        mock_insert.return_value = None  # Simulate successful database insert

        response = client.post("/v1/temperature", json=valid_mock_data)

        assert response.status_code == 201
        assert response.json() == {"message": "Temperature data added"}

    def test_add_temperature_validation_error(self, client, valid_mock_data):
        """
        Test the `add_temperature` endpoint with invalid data.

        Ensures:
        - HTTP status code is 422.
        - Validation error details are returned.
        """
        invalid_data = valid_mock_data.copy()
        invalid_data["temperature"] = 100.0  # Invalid: Out of range (-50 to 50)

        response = client.post("/v1/temperature", json=invalid_data)

        assert response.status_code == 422
        assert "detail" in response.json()

    def test_add_temperature_missing_fields(self, client):
        """
        Test the `add_temperature` endpoint with missing fields.

        Ensures:
        - HTTP status code is 422.
        - Validation error details are returned.
        """
        mock_data = {
            "building_id": "1",
            "room_id": "101",
            # Missing "temperature" and "timestamp"
        }

        response = client.post("/v1/temperature", json=mock_data)

        assert response.status_code == 422
        assert "detail" in response.json()

    @patch("app.api.v1.temperature.insert_temperature")
    def test_add_temperature_high_precision(self, mock_insert, client, valid_mock_data):
        """
        Test the `add_temperature` endpoint with high-precision temperature data.

        Ensures:
        - HTTP status code is 201.
        - A success message is returned.
        """
        mock_insert.return_value = None  # Simulate successful database insert

        high_precision_data = valid_mock_data.copy()
        high_precision_data["temperature"] = 22.555555555  # High precision

        response = client.post("/v1/temperature", json=high_precision_data)

        assert response.status_code == 201
        assert response.json() == {"message": "Temperature data added"}

    @patch("app.api.v1.temperature.insert_temperature")
    def test_add_temperature_boundary_values(
        self, mock_insert, client, valid_mock_data
    ):
        """
        Test the `add_temperature` endpoint with boundary temperature values.

        Ensures:
        - HTTP status code is 201 for valid boundary values.
        """
        mock_insert.return_value = None  # Simulate successful database insert

        for temperature in [-50, 50]:  # Boundary values
            data = valid_mock_data.copy()
            data["temperature"] = temperature

            response = client.post("/v1/temperature", json=data)

            assert response.status_code == 201
            assert response.json() == {"message": "Temperature data added"}

    @patch("app.api.v1.temperature.insert_temperature")
    def test_add_temperature_sqlalchemy_error(
        self, mock_insert, client, valid_mock_data
    ):
        """
        Test the `add_temperature` endpoint when a SQLAlchemyError occurs.

        Ensures:
        - HTTP status code is 500.
        - The error message indicates a database error.
        """
        mock_insert.side_effect = SQLAlchemyError("Database connection error")

        response = client.post("/v1/temperature", json=valid_mock_data)

        assert response.status_code == 500
        assert response.json() == {"error": "Database error occurred.", "code": 500}

    def test_add_temperature_invalid_timestamp_format(self, client, valid_mock_data):
        """
        Test the `add_temperature` endpoint with invalid timestamp format.

        Ensures:
        - HTTP status code is 422.
        - Validation error details are returned.
        """
        invalid_data = valid_mock_data.copy()
        invalid_data["timestamp"] = "01-01-2024 12:00:00"  # Invalid timestamp format

        response = client.post("/v1/temperature", json=invalid_data)

        assert response.status_code == 422
        assert "detail" in response.json()

    def test_add_temperature_large_payload(self, client, valid_mock_data):
        """
        Test the `add_temperature` endpoint with a large payload.

        Ensures:
        - HTTP status code is 422 for validation errors.
        - Proper error details are returned for excessively large payloads.
        """
        invalid_data = valid_mock_data.copy()
        invalid_data["building_id"] = "1" * 1000  # Excessively large building ID

        response = client.post("/v1/temperature", json=invalid_data)

        assert response.status_code == 422  # Validation error
        assert "detail" in response.json()
        # The exact error message may vary depending on validation rules

    def test_invalid_http_method(self, client):
        """
        Test that invalid HTTP methods are rejected.

        Ensures:
        - HTTP status code is 405 (Method Not Allowed).
        """
        response = client.put("/v1/temperature", json={})
        assert response.status_code == 405


class TestFetchAverageTemperatureEndpoint:
    """
    Test cases for the `/v1/temperature/average` endpoint.

    Includes tests for success, no data, and validation errors.
    """

    @patch("app.api.v1.temperature.get_average_temperature")
    def test_fetch_average_temperature_success(self, mock_get, client):
        """
        Test the `fetch_average_temperature` endpoint with valid query parameters.

        Ensures:
        - HTTP status code is 200.
        - The average temperature is returned.
        """
        query_params = {"building_id": "1", "room_id": "101"}
        mock_get.return_value = 21.5  # Simulated average temperature

        response = client.get("/v1/temperature/average", params=query_params)

        assert response.status_code == 200
        assert response.json() == {"average_temperature": 21.5, "message": None}

    @patch("app.api.v1.temperature.get_average_temperature")
    def test_fetch_average_temperature_no_data(self, mock_get, client):
        """
        Test the `fetch_average_temperature` endpoint when no data is found.

        Ensures:
        - HTTP status code is 200.
        - A message indicating no data is returned.
        """
        query_params = {"building_id": "1", "room_id": "101"}
        mock_get.return_value = None  # Simulate no data found

        response = client.get("/v1/temperature/average", params=query_params)

        assert response.status_code == 200
        assert response.json() == {
            "average_temperature": None,
            "message": "No data found",
        }

    def test_fetch_average_temperature_validation_error(self, client):
        """
        Test the `fetch_average_temperature` endpoint with missing query parameters.

        Ensures:
        - HTTP status code is 422.
        - Validation error details are returned.
        """
        query_params = {}  # Missing required parameters

        response = client.get("/v1/temperature/average", params=query_params)

        assert response.status_code == 422
        assert "detail" in response.json()

    @patch("app.api.v1.temperature.get_average_temperature")
    def test_fetch_average_temperature_exact_boundaries(self, mock_get, client):
        """
        Test the `fetch_average_temperature` endpoint with queries at exact boundaries.

        Ensures:
        - HTTP status code is 200.
        - Average temperature is returned correctly.
        """
        query_params = {
            "building_id": "1",
            "room_id": "101",
            "query_datetime": "2024-01-01T00:00:00",  # Exact boundary
        }
        mock_get.return_value = 25.0  # Simulated average temperature

        response = client.get("/v1/temperature/average", params=query_params)

        assert response.status_code == 200
        assert response.json() == {"average_temperature": 25.0, "message": None}


async def mock_get_db():
    """
    Mock the database dependency for testing.

    Returns:
        AsyncMock: A mocked instance of AsyncSession for testing database operations.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    yield mock_session


@pytest.mark.asyncio
@patch("app.api.v1.temperature.insert_temperature", new_callable=AsyncMock)
async def test_add_temperature_stress_test(mock_insert):
    """
    Stress test the `add_temperature` endpoint with concurrent requests.

    Simulates:
    - High traffic with 100 concurrent requests.
    - Monitors average response time and success rate.
    """
    # Override the get_db dependency
    app.dependency_overrides[get_db] = mock_get_db
    mock_insert.return_value = None  # Simulate successful database insert

    mock_data = {
        "building_id": "1",
        "room_id": "101",
        "temperature": 22.5,
        "timestamp": "2024-01-01T12:00:00",  # Use the same format as other tests
    }

    success_count = 0
    failed_count = 0
    response_times = []

    async def make_request():
        nonlocal success_count, failed_count
        start_time = time.time()
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver"
        ) as ac:
            # Add trailing slash to the endpoint
            response = await ac.post("/v1/temperature/", json=mock_data)
        response_times.append(time.time() - start_time)
        if response.status_code == 201:
            success_count += 1
        else:
            failed_count += 1
            print(
                f"Failed request with status code {response.status_code}, "
                f"response: {response.text}"
            )

    tasks = [make_request() for _ in range(100)]
    await asyncio.gather(*tasks)

    print(f"Total Requests: {len(tasks)}")
    print(f"Success: {success_count}, Failed: {failed_count}")
    print(
        "Average Response Time: "
        f"{sum(response_times) / len(response_times):.4f} seconds"
    )

    assert failed_count == 0, f"{failed_count} requests failed"
    assert success_count == 100, "Not all requests succeeded"

    # Clean up the dependency override
    app.dependency_overrides.pop(get_db, None)
