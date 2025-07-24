# 📊 Real-Time User Session Aggregation with Apache Flink, Kafka & PostgreSQL

This project implements a real-time data pipeline using **Apache Flink (PyFlink)** for processing user events streamed from **Apache Kafka**, performing **windowed session-based aggregations**, and storing the results into a **PostgreSQL** database.

## 🔧 Tech Stack

- **Apache Flink (PyFlink)** — real-time stream processing
- **Apache Kafka** — event streaming platform
- **PostgreSQL** — relational database for storing aggregates
- **Docker** — containerized development environment
- **Python** — Flink jobs written in PyFlink

---

## 🚀 Features

- Ingests user interaction events (JSON) from a Kafka topic (`app_events`)
- Extracts session information using **5-minute tumbling windows**
- Aggregates:
  - Total user actions
  - Whether the user logged in during the session
  - Whether a purchase was made
- Persists aggregated results into a PostgreSQL table (`apple_app_aggregates`)
- Supports fault tolerance with **checkpointing** enabled in Flink

---


---

## 🧠 How It Works

1. **Kafka source** (`user_events` table in Flink):
   - Reads messages containing: `user_id`, `action`, `event_time_raw`, `device`
   - Extracts processing timestamp (`event_time`) and assigns watermarks

2. **Windowed Aggregation**:
   - Groups by `user_id`, `device`, and 5-minute tumbling windows
   - Evaluates session KPIs:
     - `session_duration`
     - `did_login`, `did_purchase` flags
     - `total_actions`

3. **PostgreSQL sink**:
   - Writes output rows to `apple_app_aggregates` using Flink’s JDBC connector

---

## ✅ Sample Aggregation Output

| user_id | session_id        | session_start      | device | did_login | did_purchase | total_actions |
|---------|-------------------|--------------------|--------|-----------|---------------|----------------|
| 123     | 123_20250724120000 | 2025-07-24 12:00:00 | iPhone | true      | false         | 5              |


## 🛠️ Project Setup Details

- **PostgreSQL** is running locally on the host machine.
  - Connection URL: `jdbc:postgresql://host.docker.internal:5432/postgres`
  - Username: `postgres`
  - Password: `poni`

- **Apache Flink** and **Apache Kafka** are running inside Docker containers.

> **Note:**  
> Since Postgres runs outside Docker, the Flink container connects to it using `host.docker.internal` to reach the local host machine from within Docker networking.  
> Make sure your local Postgres is configured to accept connections from Docker containers (check `pg_hba.conf` and firewall rules).

This setup allows separation of services and simulates a realistic environment with streaming components containerized, while the database remains on your local system for easy access and debugging.

## 🚀 How to Run the Project

Follow these steps to get your real-time aggregation pipeline up and running.

### 1. Start the Kafka Producer

- Ensure Kafka and ZooKeeper services are running (e.g., via Docker Compose).
- Start producing user event messages to the Kafka topic `app_events`.

Example JSON event message:
{
"user_id": 123,
"action": "login",
"event_time_raw": "2025-07-24T12:01:00.000",
"device": "iPhone"
}

### 2. Run the Flink Aggregation Job

Make sure Kafka, ZooKeeper, and PostgreSQL are running.

Run your PyFlink job locally with:


---

. Important: Update Aggregation Logic

Whenever you modify the aggregation query or PyFlink job:

- Save your changes.
- Restart or redeploy the Flink job to apply updates.
- If running via CLI, stop the old job and submit the updated one.
- Flink does **not** hot-reload code changes automatically.

**Note:** Always make sure to re-run your Flink job after changes to see their effect in processing.

---

### Summary Workflow

1. Start Kafka, ZooKeeper, and PostgreSQL services.
2. Run your Kafka producer to send user events.
3. Execute the Flink PyFlink aggregation job.
4. Check results in PostgreSQL.
5. After any code change, redeploy/restart the Flink job.










