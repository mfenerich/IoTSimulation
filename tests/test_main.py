"""
Test suite for FastAPI IoT API.

This module contains tests for the health and settings endpoints of the
    FastAPI application.

Tests:
- `test_read_item`: Validates the `/health` endpoint for basic functionality.
- `test_get_settings`: Validates the `/settings` endpoint for correctness of
    application settings.
- `test_health_response_time`: Ensures the `/health` endpoint responds within an
    acceptable time frame.
- `test_health_content_type`: Verifies that the `/health` endpoint returns the
    correct content type.
- `test_health_stress`: Simulates multiple requests to the `/health` endpoint to
    test stability under load.
"""

import time

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

# Initialize TestClient for FastAPI app
client = TestClient(app)


def test_read_item():
    """
    Test the `/health` endpoint for basic functionality.

    Validates:
    - HTTP status code is 200.
    - JSON response contains `{"status": "ok", "message": "Service is healthy"}`.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Service is healthy"}


def test_get_settings():
    """
    Test the `/settings` endpoint to ensure application settings are returned correctly.

    Validates:
    - HTTP status code is 200.
    - JSON response contains `app_name` and `debug` fields matching the loaded settings.
    """
    # Make a GET request to the `/settings` endpoint
    response = client.get("/settings")

    # Assert that the status code is 200
    assert response.status_code == 200

    # Validate the response data
    expected_response = {
        "app_name": settings.app_name,
        "debug": settings.debug,
    }
    assert response.json() == expected_response


def test_health_response_time():
    """
    Test the response time of the `/health` endpoint.

    Ensures:
    - HTTP status code is 200.
    - Response time is less than 200 milliseconds.
    """
    start_time = time.time()
    response = client.get("/health")
    end_time = time.time()

    assert response.status_code == 200
    assert (end_time - start_time) < 0.2  # Response should take less than 200ms


def test_health_content_type():
    """
    Test the content type of the `/health` endpoint response.

    Ensures:
    - HTTP status code is 200.
    - `Content-Type` header is `application/json`.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "application/json"


def test_health_stress():
    """
    Test the stability of the `/health` endpoint under high request load.

    Simulates:
    - 100 consecutive GET requests to the `/health` endpoint.
    Validates:
    - All requests return HTTP status code 200.
    """
    for _ in range(100):  # Simulate 100 requests
        response = client.get("/health")
        assert response.status_code == 200


def test_http_exception_handler():
    """
    Test the custom HTTPException handler.

    Simulate a scenario where an invalid request triggers an HTTPException.
    """
    response = client.get("/v1/temperature/some-invalid-endpoint")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
