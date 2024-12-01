# IoT Temperature API

## Overview

The **IoT Temperature API** is a FastAPI-based application designed to manage temperature data for IoT systems. It provides a suite of endpoints to add temperature data, fetch average temperatures, and retrieve system health and settings. 

This README provides details about the application, its features, and instructions for usage.

---

## Features

- **Temperature Management**:
  - Add temperature data for buildings and rooms.
  - Fetch average temperature data for specific time ranges.

- **Health Check**:
  - Verify the health of the application with a dedicated endpoint.

- **Application Settings**:
  - Retrieve runtime configuration, such as app name and debug mode status.

- **Robust Error Handling**:
  - Custom exception handlers for HTTP and unexpected errors.

---

## API Documentation

### Base URL
The API is hosted at:  
`http://<host>:<port>/`

### Endpoints

#### Health Check

**GET** `/health`

- **Description**: Checks the health status of the service.
- **Response**:
  - Status: 200 OK
  - Body:
    ```json
    {
      "status": "ok",
      "message": "Service is healthy"
    }
    ```

---

#### Temperature Management

The **Temperature Management** endpoints are available under the `/v1/temperature` prefix. Refer to the specific router documentation for more details.

---

#### Application Settings

**GET** `/settings`

- **Summary**: Retrieve application runtime settings.
- **Response Model**: `SettingsResponse`
  - `app_name` (string): The name of the application.
  - `debug` (boolean): Indicates whether the application is running in debug mode.

---

### Exception Handling

- **HTTP Exceptions**:
  Logs and responds with standardized JSON for HTTP errors.
  ```json
  {
    "error": "Detailed error message",
    "code": <HTTP status code>
  }
  ```

- **Generic Exceptions**:
  Handles unexpected errors gracefully with a 500 response.
  ```json
  {
    "error": "An unexpected error occurred. Please try again later.",
    "code": 500
  }
  ```

---

## Application Configuration

The application is configured using the `app.core.config` module. You can modify settings such as `app_name`, `debug`, and other configurations as needed.

---

## Lifespan Hooks

Custom startup and shutdown logic is handled using an asynchronous lifespan context.  
- **Startup**: Logs the initialization of the service.
- **Shutdown**: Logs the termination of the service.

---

## Running the Application

### Prerequisites

- **Python**: Version 3.9 or later.
- **Dependencies**: Install via `requirements.txt`.

```bash
pip install -r requirements.txt
```

### Running Locally

Run the application using `uvicorn`:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

---

## Contact

For support or inquiries, contact:

- **Name**: API Support  
- **URL**: [feneri.ch](http://feneri.ch)  
- **Email**: [marcel@feneri.ch](mailto:marcel@feneri.ch)  

---

## License

This project is licensed under the **MIT License**.  
For details, see the [LICENSE](https://opensource.org/licenses/MIT) file.

---

## Additional Information

- **API Documentation**: The API's interactive Swagger UI is available at `/docs`, and ReDoc documentation can be accessed at `/redoc`.
- **Version**: `1.0.0`
- **Terms of Service**: [Terms of Service](http://example.com/terms/).