Backend Developer Technical Assessment

Overview:
A containerized data pipeline consisting of a Flask Mock Server, a PostgreSQL database, and a FastAPI Ingestion Service.

Architecture:
Mock Server (Port 5000): Flask API serving customer data from `customers.json`.
Pipeline Service (Port 8000): FastAPI application using `dlt` for ELT (Extract, Load, Transform) processes.
Database (Port 5432): PostgreSQL instance for persistent storage.

Key Features:
Idempotent Ingestion: Uses `dlt` with `write_disposition="merge"` to ensure no duplicate records on multiple runs.
Paginated Results: Both Flask and FastAPI endpoints support consistent pagination metadata.

How to Run:
Quick Start
To spin up the entire environment and run the ingestion:

1. Start Services: docker-compose up -d --build
2. Run Ingestion: curl -X POST http://localhost:8000/api/ingest
3. Verify Data: curl "http://localhost:8000/api/customers?page=1&limit=5"
4. Verify the Destination (FastAPI + Postgres): curl "http://localhost:8000/api/customers"

Architecture:
1.	The system follows a microservices pattern orchestrated by Docker Compose:
2.	Mock Server (Flask): Serves source data from customers.json. Implements custom pagination logic.
3.	Pipeline Service (FastAPI): Acts as the ETL engine. It extracts data from the Flask API, transforms it for database compatibility, and loads it into PostgreSQL.
4.	Database (PostgreSQL 15): Persistent storage for ingested customer records.

Key Technical Decisions:
Data Ingestion with dlt
1.	Instead of writing manual SQL INSERT statements, I utilized the Data Load Tool (dlt) library.
2.	Idempotency: Using write_disposition="merge" with customer_id as a primary key ensures that running the ingestion multiple times does not create duplicate records.
3.	Schema Evolution: dlt automatically infers the schema from the JSON source and maps it to the SQLAlchemy-defined table.
4.	Resilience: The pipeline handles auto-pagination from the source API, ensuring memory efficiency even if the dataset grows significantly.


Data Flow Breakdown
1.  Extraction: The FastAPI service requests data from the Flask Mock Server.
2.  Transformation: Data is cleaned (date/time parsing) within a Python generator to keep the memory footprint low.
3.  Loading: The `dlt` engine performs a "Merge" (Upsert) operation into PostgreSQL.


API Specification
Flask Mock Server (Port 5000)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/customers` | GET | Returns paginated JSON from file. Params: `page`, `limit`. |
| `/api/customers/{id}` | GET | Returns single customer or 404. |
| `/api/health` | GET | Service status check. |

Pipeline Service (Port 8000)
| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/ingest` | POST | Triggers the ETL pipeline from Flask to Postgres. |
| `/api/customers` | GET | Returns paginated data **from the database**. |
| `/api/customers/{id}` | GET | Returns single customer from the database. |
