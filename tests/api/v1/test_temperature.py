import asyncio
from fastapi.testclient import TestClient
from app.main import app

from unittest.mock import patch, AsyncMock
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
import pytest
import time
from httpx import AsyncClient, ASGITransport
from app.core.dependencies import get_db

# Initialize TestClient for FastAPI app
client = TestClient(app)

def test_add_temperature_success():
    """
    Test the `add_temperature` endpoint with valid data.

    Ensures:
    - HTTP status code is 201.
    - A success message is returned.
    """
    mock_data = {
        "building_id": "1",
        "room_id": "101",
        "temperature": 22.5,
        "timestamp": "2024-01-01T12:00:00",
    }

    with patch("app.api.v1.temperature.insert_temperature") as mock_insert:
        mock_insert.return_value = None  # Simulate successful database insert
        
        response = client.post("/v1/temperature", json=mock_data)
        
        assert response.status_code == 201
        assert response.json() == {"message": "Temperature data added"}

def test_add_temperature_validation_error():
    """
    Test the `add_temperature` endpoint with invalid data.

    Ensures:
    - HTTP status code is 422.
    - Validation error details are returned.
    """
    mock_data = {
        "building_id": "1",
        "room_id": "101",
        "temperature": 100.0,  # Invalid: Out of range (-50 to 50)
        "timestamp": "2024-01-01T12:00:00",
    }
    
    response = client.post("/v1/temperature", json=mock_data)
    
    assert response.status_code == 422
    assert "detail" in response.json()


def test_add_temperature_missing_fields():
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

def test_fetch_average_temperature_success():
    """
    Test the `fetch_average_temperature` endpoint with valid query parameters.

    Ensures:
    - HTTP status code is 200.
    - The average temperature is returned.
    """
    query_params = {"building_id": "1", "room_id": "101"}
    
    with patch("app.api.v1.temperature.get_average_temperature") as mock_get:
        mock_get.return_value = 21.5  # Simulated average temperature
        
        response = client.get("/v1/temperature/average", params=query_params)
        
        assert response.status_code == 200
        assert response.json() == {"average_temperature": 21.5, "message": None}

def test_fetch_average_temperature_no_data():
    """
    Test the `fetch_average_temperature` endpoint when no data is found.

    Ensures:
    - HTTP status code is 200.
    - A message indicating no data is returned.
    """
    query_params = {"building_id": "1", "room_id": "101"}
    
    with patch("app.api.v1.temperature.get_average_temperature") as mock_get:
        mock_get.return_value = None  # Simulate no data found
        
        response = client.get("/v1/temperature/average", params=query_params)
        
        assert response.status_code == 200
        assert response.json() == {"average_temperature": None, "message": "No data found"}


def test_fetch_average_temperature_validation_error():
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

def test_invalid_http_method():
    """
    Test that invalid HTTP methods are rejected.

    Ensures:
    - HTTP status code is 405 (Method Not Allowed).
    """
    response = client.put("/v1/temperature", json={})
    assert response.status_code == 405

def test_add_temperature_high_precision():
    """
    Test the `add_temperature` endpoint with high-precision temperature data.

    Ensures:
    - HTTP status code is 201.
    - A success message is returned.
    """
    mock_data = {
        "building_id": "1",
        "room_id": "101",
        "temperature": 22.555555555,  # High precision
        "timestamp": "2024-01-01T12:00:00",
    }

    with patch("app.api.v1.temperature.insert_temperature") as mock_insert:
        mock_insert.return_value = None  # Simulate successful database insert
        
        response = client.post("/v1/temperature", json=mock_data)
        
        assert response.status_code == 201
        assert response.json() == {"message": "Temperature data added"}

def test_add_temperature_boundary_values():
    """
    Test the `add_temperature` endpoint with boundary temperature values.

    Ensures:
    - HTTP status code is 201 for valid boundary values.
    """
    for temperature in [-50, 50]:  # Boundary values
        mock_data = {
            "building_id": "1",
            "room_id": "101",
            "temperature": temperature,
            "timestamp": "2024-01-01T12:00:00",
        }

        with patch("app.api.v1.temperature.insert_temperature") as mock_insert:
            mock_insert.return_value = None  # Simulate successful database insert
            
            response = client.post("/v1/temperature", json=mock_data)
            
            assert response.status_code == 201
            assert response.json() == {"message": "Temperature data added"}

def test_add_temperature_sqlalchemy_error():
    """
    Test the `add_temperature` endpoint when a SQLAlchemyError occurs.

    Ensures:
    - HTTP status code is 500.
    - The error message indicates a database error.
    """
    mock_data = {
        "building_id": "1",
        "room_id": "1",
        "temperature": 22.5,
        "timestamp": "2024-01-01T12:00:00",
    }

    with patch("app.api.v1.temperature.insert_temperature") as mock_insert:
        mock_insert.side_effect = SQLAlchemyError("Database connection error")
        
        response = client.post("/v1/temperature", json=mock_data)
        
        assert response.status_code == 500
        assert response.json() == {'error': 'Database error occurred.', 'code': 500}

def test_add_temperature_missing_db_connection():
    """
    Test the `add_temperature` endpoint when the database connection is unavailable.

    Ensures:
    - HTTP status code is 500.
    - The error message indicates a database connection error.
    """
    mock_data = {
        "building_id": "1",
        "room_id": "101",
        "temperature": 22.5,
        "timestamp": "2024-01-01T12:00:00",
    }

    with patch("app.api.v1.temperature.insert_temperature") as mock_insert:
        mock_insert.side_effect = SQLAlchemyError("Database connection error")
        
        response = client.post("/v1/temperature", json=mock_data)
        
        assert response.status_code == 500
        assert response.json() == {'error': 'Database error occurred.', 'code': 500}

def test_add_temperature_invalid_timestamp_format():
    """
    Test the `add_temperature` endpoint with invalid timestamp format.

    Ensures:
    - HTTP status code is 422.
    - Validation error details are returned.
    """
    mock_data = {
        "building_id": "1",
        "room_id": "101",
        "temperature": 22.5,
        "timestamp": "01-01-2024 12:00:00",  # Invalid timestamp format
    }
    
    response = client.post("/v1/temperature", json=mock_data)
    
    assert response.status_code == 422
    assert "detail" in response.json()

def test_fetch_average_temperature_exact_boundaries():
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
    
    with patch("app.api.v1.temperature.get_average_temperature") as mock_get:
        mock_get.return_value = 25.0  # Simulated average temperature
        
        response = client.get("/v1/temperature/average", params=query_params)
        
        assert response.status_code == 200
        assert response.json() == {"average_temperature": 25.0, "message": None}

def test_add_temperature_large_payload():
    """
    Test the `add_temperature` endpoint with a large payload.

    Ensures:
    - HTTP status code is 422 for validation errors.
    - Proper error details are returned for excessively large payloads.
    """
    mock_data = {
        "building_id": "1" * 1000,  # Excessively large building ID
        "room_id": "101",
        "temperature": 22.5,
        "timestamp": "2024-01-01T12:00:00Z",
    }
    
    response = client.post("/v1/temperature", json=mock_data)
    
    assert response.status_code == 422  # Validation error
    assert "detail" in response.json()
    assert response.json()["detail"][0]["msg"] == "String should have at most 255 characters"

# Mock the get_db dependency
async def mock_get_db():
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
                transport=ASGITransport(app=app),
                base_url="http://testserver"
            ) as ac:
            # Add trailing slash to the endpoint
            response = await ac.post("/v1/temperature/", json=mock_data)
        response_times.append(time.time() - start_time)
        if response.status_code == 201:
            success_count += 1
        else:
            failed_count += 1
            print(f"Failed request with status code {response.status_code}, response: {response.text}")

    tasks = [make_request() for _ in range(100)]
    await asyncio.gather(*tasks)

    print(f"Total Requests: {len(tasks)}")
    print(f"Success: {success_count}, Failed: {failed_count}")
    print(f"Average Response Time: {sum(response_times) / len(response_times):.4f} seconds")

    assert failed_count == 0, f"{failed_count} requests failed"
    assert success_count == 100, "Not all requests succeeded"

    # Clean up the dependency override
    app.dependency_overrides.pop(get_db, None)
