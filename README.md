# Temperature Monitoring Service

This project implements a backend service for ingesting, storing, and analyzing temperature data from multiple buildings and rooms. It showcases practical techniques for handling time-series data in an IoT-like environment, leveraging **TimescaleDB** and **Kubernetes** for scalability and efficiency.

---

## **Important Disclaimer**

🚨 **This project is specifically designed to be deployed on macOS systems with an ARM64 architecture.**  

While the code and configuration may work on other platforms, the setup, tooling, and dependencies (such as Docker images and Kubernetes configurations) have been optimized and tested exclusively on **macOS ARM64**. If you are using a different operating system or architecture, additional modifications may be required to ensure compatibility.  

---

## Overview

The solution consists of two main services:

1. **API Service**:
   - A RESTful API that provides the following endpoints:
     - **POST /temperature**: Accepts temperature readings in the following format:
       ```json
       {
         "building_id": "B1",
         "room_id": "101",
         "temperature": 22.5,
         "timestamp": "2024-12-01T12:34:56.000Z"
       }
       ```
     - **GET /temperature/average**: Retrieves the average temperature for a specific building and room over a given time interval.

2. **Simulation Service**:
   - Runs in its own Kubernetes pod and generates random temperature readings between -50°C and 50°C for predefined buildings and rooms:
     ```python
     [
         ("B1", "101"),
         ("B1", "102"),
         ("B2", "201"),
     ]
     ```
   - Sends these readings to the API to simulate real-world IoT data streams.

---

## Database Design and Strategy

The project uses **TimescaleDB**, a PostgreSQL extension optimized for time-series data, to efficiently handle continuous data streams and perform aggregations.

### Why TimescaleDB?

- **Time-Series Optimization**: Handles high-frequency inserts and queries efficiently.
- **Continuous Aggregates**: Precomputes summaries for time windows, reducing computational overhead.
- **Familiarity**: Built on PostgreSQL, enabling developers to leverage existing SQL expertise.

### Schema and Aggregation Strategy

Temperature readings are stored in a `temperatures` table, with **continuous aggregates** used to calculate rolling averages over time intervals.

#### Continuous Aggregate Creation:
```sql
CREATE MATERIALIZED VIEW avg_temperature_time_interval
WITH (timescaledb.continuous) AS
SELECT time_bucket('2 minutes', timestamp) AS bucket, -- Group data into 2-minute intervals
       building_id,
       room_id,
       AVG(temperature) AS avg_temp -- Compute average temperature
FROM temperatures
GROUP BY bucket, building_id, room_id
WITH NO DATA; -- Defer initial computation for faster creation
```

> **Note**: For production, a 15-minute interval is recommended. The 2-minute interval is used here to provide quicker feedback during testing.

#### Continuous Aggregate Policy:
```sql
SELECT add_continuous_aggregate_policy('avg_temperature_time_interval',
    start_offset => INTERVAL '1 hour',
    end_offset => INTERVAL '10 seconds',
    schedule_interval => INTERVAL '5 seconds'); -- Frequent updates for demonstration
```

- **Explanation**: This policy ensures aggregates remain up-to-date by incrementally processing changes in the underlying data.

---

## Logging and Monitoring

To facilitate system monitoring and debugging, this project generates an **`app.log`** file where all system logs are stored. This log file includes details about API activity, system errors, and general performance metrics.

### Key Features of `app.log`:
- Provides a comprehensive history of system operations.
- Useful for troubleshooting errors and monitoring API performance.
- Designed to support future monitoring integrations like ELK (Elasticsearch, Logstash, Kibana) or Grafana.

The log file is stored in the root directory of the application and is automatically updated during runtime.

---

## Deployment Architecture

The project uses **Kind** (Kubernetes in Docker) for local testing and deployment, with Kubernetes managing both the API and simulation services.

Additionally, the integration of logging via app.log ensures the system is well-prepared for monitoring and debugging. 

---

## Prerequisites

### Required Tools and Dependencies
1. **Docker**: Used for containerizing and running the services.
   - Installation: [Docker Documentation](https://docs.docker.com/get-docker/)
2. **Homebrew**: A package manager for macOS, used to install other tools like `kubectl`.
3. **Kubectl**: Command-line tool to interact with Kubernetes.
   - Installation via Homebrew:
     ```bash
     brew install kubectl
     ```
   - **Note**: The `Makefile` automatically installs `kubectl` if not already installed.
4. **GNU Make**: Used to simplify and automate deployment tasks.
   - Installation via Homebrew:
     ```bash
     brew install make
     ```

## **Important Disclaimer: Docker Resource Configuration**

🚨 **Resource Requirements**:  
Some environments may require more system resources to run this project efficiently, especially when handling high-frequency IoT data streams or managing multiple Kubernetes pods.

### **Recommended Docker Configuration**
To ensure smooth operation, it is recommended to configure your Docker environment with the following resources:
- **CPU Limit**: 4 cores
- **Memory Limit**: 6 GB
- **Swap**: 2 GB
- **Virtual Disk Space**: 120 GB

You can adjust these settings in your Docker Desktop preferences under **Resources**. Properly configuring these resources will help avoid performance bottlenecks or crashes, especially during the build or deployment phases.

💡 **Tip**: If you're running Docker on macOS ARM64, these settings have been tested to work well under typical project workloads.

---

## Setup and Deployment

### Clone the Repository
```bash
cd IoTSimulation-main
```

### Build and Deploy Locally
```bash
make build
```
This performs the following tasks:
- Builds and pushes the Docker image.
- Creates the Kind cluster and local registry configuration.
- Deploys all Kubernetes resources, including:
  - Postgres Operator.
  - TimescaleDB cluster.
  - Application services.

### Notes on Deployment
- A local Docker registry is used to push and pull images locally. 

> **Note**: I initially intended to create my own local Docker registry to build and pull everything locally. However, due to licensing constraints, I had to build my own TimescaleDB image based on Zalando's implementation. Since the build process for this type of image is complex and resource-intensive, I opted to pull it from my public Docker Hub instead. About the the local Docker registry I have something on my [personal blog](https://feneri.ch/kubernetes/2024/10/21/k8s-project-creating-a-local-docker-registry-part-iii.html).

---

## Verifying Deployment

### Monitor Pods
```bash
kubectl get po
```

The system will be ready to use when you see something like this:
```bash
NAME                                 READY   STATUS    RESTARTS       AGE
acid-minimal-cluster-0               1/1     Running   0              12m
iotsimulator-7cddff8495-qb847        2/2     Running   0              12m
postgres-operator-69c58b594c-lml2n   1/1     Running   1 (12m ago)    12m
```

### Access the API
- API Endpoint: `http://localhost:30080/v1/temperature/average?building_id=B1&room_id=101`
- **Note**: The first results will take approximately 2 minutes to appear, as the system needs to process the initial time bucket.

### Auto-Generated API Documentation
- Swagger UI: [http://localhost:30080/docs](http://localhost:30080/docs)
- ReDoc: [http://localhost:30080/redoc](http://localhost:30080/redoc)

### Connecting to the Database
1. Forward the PostgreSQL pod port to your local machine:
   ```bash
   kubectl port-forward pod/acid-minimal-cluster-0 5432:5432
   ```
2. Connect using PostgreSQL credentials:
   ```bash
   user: postgres
   pass: password
   ```
3. Example Queries:
   - Retrieve raw temperature data:
     ```sql
     SELECT * FROM temperatures;
     ```
   - View aggregated temperature averages:
     ```sql
     SELECT *
     FROM avg_temperature_time_interval
     ORDER BY bucket DESC;
     ```

---

## Testing

### Running Tests Locally
```bash
poetry install
poetry run pytest
```

---

## Teardown

To clean up the deployment and Kind cluster:
```bash
make delete_kind_cluster
```

---

## CI/CD Pipelines

This project includes a robust CI/CD pipeline implemented using **GitHub Actions**. The pipeline ensures code quality and testing are maintained at every push, improving reliability and streamlining the development process.

### Pipeline Overview

The pipeline is defined in `.github/workflows/pipeline.yml` and consists of two main jobs:

1. **Code Quality Check**:
   - **Purpose**: Ensures that the code adheres to style guidelines and passes pre-commit hooks.
   - **Steps**:
     - Checks out the repository code.
     - Sets up a Python environment using a custom GitHub Action (`setup-environment`).
     - Installs dependencies using Poetry.
     - Runs `ruff` (a fast Python linter) through pre-commit hooks to validate code quality.
   - **Dependencies**:
     - Pre-commit hooks are configured to run automatically during this step.

2. **Run Tests**:
   - **Purpose**: Executes all unit tests to validate the codebase.
   - **Steps**:
     - Waits for the `code-quality` job to complete.
     - Checks out the repository code.
     - Sets up a Python environment using the same custom GitHub Action.
     - Installs dependencies using Poetry.
     - Runs the test suite with `pytest`.
   - **Environment Variables**:
     - Critical configuration values like `DATABASE_URL`, `POSTGRES_USER`, and `POSTGRES_PASSWORD` are passed via environment variables for test execution. Secrets should ideally be stored securely using GitHub's environment variables and secrets management.

### Custom GitHub Action: `setup-environment`

A custom composite action (`action.yaml`) is used to standardize the Python environment setup. This action simplifies the pipeline by handling the installation of specific Python and Poetry versions and caching dependencies for faster builds.

#### `action.yaml`
- **Inputs**:
  - `python-version`: Specifies the Python version to be used (default: 3.11).
  - `poetry-version`: Specifies the Poetry version to be used (default: 1.8.3).
- **Steps**:
  - Installs the specified Poetry version using `pipx`.
  - Sets up the specified Python version using the `actions/setup-python` action, with Poetry package caching enabled.

### Trigger

The pipeline is triggered on every `push` event to the repository.

---

## Why These Technologies?

In this project, I’ve chosen a set of modern tools and frameworks to make the backend fast, scalable, and easy to work with.

### **FastAPI**
- **Why FastAPI?**
  Powerful and developer-friendly. It’s super fast (thanks to Python’s async capabilities) and makes it ridiculously easy to define APIs. It also automatically generates Swagger and ReDoc documentation.

- **Why It Fits This Project**:
  FastAPI’s performance and asynchronous support keep everything running smoothly.

---

### **Uvicorn**
- **Why Uvicorn?**
  It’s an ASGI server, which means it’s optimized for handling asynchronous tasks, exactly what is needed for a project like this, where requests can come in thick and fast.

- **Why It Fits This Project**:
  It works seamlessly with FastAPI to deliver high performance and low latency.

---

### **SQLAlchemy**
- **Why SQLAlchemy?**
  When it comes to interacting with a database, SQLAlchemy strikes the perfect balance between power and flexibility. It’s like having the best of both worlds: a Pythonic ORM for when you want to work with objects and raw SQL for when you need precise control, just like happened on this project.

- **Why It Fits This Project**:
  It’s great for working with PostgreSQL, which is the backbone of this project.

---

### **Alembic**
- **Why Alembic?**
  Let’s face it: managing database schema changes manually is a pain. That’s where Alembic comes in. It keeps track of every schema update, making database migrations as smooth as butter.

- **Why It Fits This Project**:
  As the project evolves, I need a reliable way to update the database schema without breaking anything. Alembic makes this process almost effortless, letting me focus on the fun stuff—like coding!

---

## Conclusion

This project demonstrates a scalable and efficient approach to handling time-series data in an IoT environment. By leveraging **TimescaleDB** for data aggregation and **Kubernetes** for deployment, it balances simplicity with performance. This setup serves as a solid foundation for more complex IoT systems, including real-time analytics and event-driven architectures.

Feel free to explore the code, test the setup, and share your feedback!