Your updated README is detailed and covers most of the necessary aspects for setting up, deploying, and using the service. Below is a slightly refined version, improving clarity and formatting:

---

# Temperature Monitoring Service

This project implements a backend service for ingesting, storing, and analyzing temperature data from multiple buildings and rooms. It showcases practical techniques for handling time-series data in an IoT-like environment, leveraging **TimescaleDB** and **Kubernetes** for scalability and efficiency.

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

## Deployment Architecture

The project uses **Kind** (Kubernetes in Docker) for local testing and deployment, with Kubernetes managing both the API and simulation services.

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

## Conclusion

This project demonstrates a scalable and efficient approach to handling time-series data in an IoT environment. By leveraging **TimescaleDB** for data aggregation and **Kubernetes** for deployment, it balances simplicity with performance. This setup serves as a solid foundation for more complex IoT systems, including real-time analytics and event-driven architectures.

Feel free to explore the code, test the setup, and share your feedback!