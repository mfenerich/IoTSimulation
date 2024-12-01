# Temperature Monitoring Service

This project implements a backend service for ingesting, storing, and analyzing temperature data from multiple buildings and rooms. It showcases practical techniques for handling time-series data in an IoT-like environment, leveraging TimescaleDB and Kubernetes for scalability and efficiency.

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

- **Time-Series Optimization**: Efficiently handles high-frequency inserts and queries.
- **Continuous Aggregates**: Precomputes summaries for time windows, reducing computational overhead.
- **Familiarity**: Built on PostgreSQL, allowing developers to leverage existing SQL expertise.

### Schema and Aggregation Strategy

Temperature readings are stored in a `temperatures` table, with continuous aggregates used to calculate rolling averages over time intervals.

#### Continuous Aggregate Creation:
```sql
CREATE MATERIALIZED VIEW avg_temperature_time_interval
WITH (timescaledb.continuous) AS
SELECT time_bucket('2 minutes', timestamp) AS bucket, -- Group data into 15-minute (read 2) intervals
       building_id,
       room_id,
       AVG(temperature) AS avg_temp -- Compute average temperature
FROM temperatures
GROUP BY bucket, building_id, room_id
WITH NO DATA; -- Defer initial computation for faster creation
```

> **Note**: For production, a 15-minute interval is recommended. The 2-minute interval here is for quicker feedback during testing.

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

### Deployment Steps

1. **Set Up Kind Cluster**:
   - A local Kubernetes cluster is created using Kind.
   - Automated via the `Makefile` for ease of setup.

2. **Deploy Services**:
   - API and simulation services are deployed as separate pods.
   - **Zalando Postgres Operator** is used to initialize TimescaleDB with the required schema and policies.

3. **Automation**:
   - The `Makefile` simplifies cluster setup, service deployment, and teardown:
     ```bash
     make build
     ```

4. **Monitor Pod Status**:
   - Check the status of all pods to ensure they are running:
     ```bash
     kubectl get po
     ```
   - Example output when all pods are ready:
     ```bash
     NAME                                 READY   STATUS    RESTARTS   AGE
     acid-minimal-cluster-0               1/1     Running   0          74m
     iotsimulator-7cddff8495-qb847        2/2     Running   0          74m
     postgres-operator-69c58b594c-lml2n   1/1     Running   1          75m
     ```

5. **Access the API**:
   - API Service: `http://localhost:30080/v1/temperature/average?building_id=B1&room_id=101`
   - The simulation service will automatically generate and ingest temperature data.

---

## Testing Strategy

1. **Unit Tests**:
   - Validate API endpoints for:
     - Input validation.
     - Correct database operations.
     - Handling of edge cases.

2. **Simulation Validation**:
   - Verify that the simulation service generates data correctly.
   - Ensure API ingestion works as expected.

3. **Performance Testing**:
   - Simulate high-frequency data ingestion.

4. **Integration Tests**:
   - These would be a great addition for end-to-end validation in future iterations.

### Running Tests
To run tests locally:
```bash
poetry install
poetry run pytest
```

---

## Considerations and Trade-Offs

1. **Database Selection**:
   - While TimescaleDB is powerful for time-series data, alternatives like Apache Kafka (for event streaming) or InfluxDB (for time-series storage) may handle higher throughput for IoT applications.

2. **Scalability**:
   - The current architecture is designed for simplicity and demonstration. Adding tools like Kafka for streaming or Grafana for visualization can enhance scalability and usability.

---

## How to Get Started

### Prerequisites
- Docker
- Kubernetes (Kind)
- Python 3.12+
- Make

### Setup and Deployment

1. Clone the repository:
   Unzip the provided file.
   ```bash
   cd IoTSimulation-main
   ```

2. Build and deploy locally:
   ```bash
   make build
   ```

3. Monitor pods and ensure all services are running:
   ```bash
   kubectl get po
   ```

4. Access the API:
   - API Endpoint: `http://localhost:30080/v1/temperature/average?building_id=B1&room_id=101`

### Check auto-generated API's documentation
```bash
http://localhost:30080/docs
http://localhost:30080/redoc
```

### Connecting to database:
Run the k8s port-forward and connect normaly to the database using postgres or timescales's drivers:
```bash
kubectl port-forward pod/acid-minimal-cluster-0 5432:5432
```

```bash
user: postgres
pass: password
```

---

## Conclusion

This project demonstrates a scalable and efficient approach to handling time-series data in an IoT environment. By leveraging TimescaleDB for data aggregation and Kubernetes for deployment, it balances simplicity with performance. This setup can serve as a foundation for more complex IoT systems, including real-time analytics and event-driven architectures.

Feel free to explore the code, test the setup, and share your feedback!