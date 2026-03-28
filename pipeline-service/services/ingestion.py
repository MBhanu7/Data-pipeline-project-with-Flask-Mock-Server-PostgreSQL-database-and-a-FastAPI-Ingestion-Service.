import dlt
import requests
import os
from datetime import datetime

def run_dlt_pipeline():
    def fetch_from_flask():
        page, limit = 1, 10
        while True:
            response = requests.get(f"http://mock-server:5000/api/customers?page={page}&limit={limit}")
            response.raise_for_status()
            data = response.json().get('data', [])
            if not data: 
                break

            for r in data:
                # Clean Date and Timestamp formats for Postgres
                if r.get("date_of_birth"):
                    r["date_of_birth"] = datetime.strptime(r["date_of_birth"], "%Y-%m-%d").date()
                if r.get("created_at"):
                    r["created_at"] = datetime.strptime(r["created_at"].replace("Z", "+0000"), "%Y-%m-%dT%H:%M:%S%z")

            yield data
            if len(data) < limit: 
                break
            page += 1

    db_url = os.getenv("DATABASE_URL")
    pipeline = dlt.pipeline(
        pipeline_name="flask_to_postgres", 
        destination=dlt.destinations.postgres(credentials=db_url), # FIX: Use credentials directly
        dataset_name="public"
    )

    return pipeline.run(
        fetch_from_flask(), 
        table_name="customers", 
        write_disposition="merge", 
        primary_key="customer_id"
    )