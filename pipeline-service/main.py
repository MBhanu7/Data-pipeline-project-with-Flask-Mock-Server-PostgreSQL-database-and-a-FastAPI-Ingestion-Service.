from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import Base, engine, get_db
from models.customer import Customer
from services.ingestion import run_dlt_pipeline

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/api/ingest")
def ingest_data(db: Session = Depends(get_db)):
    try:
        # Run the DLT ingestion pipeline
        run_dlt_pipeline()
        
        # Count the records now in the database
        total_records = db.query(Customer).count()
        
        return {
            "status": "success", 
            "records_processed": total_records
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers")
def get_customers(
    page: int = Query(1, ge=1), 
    limit: int = Query(10, ge=1, le=100), 
    db: Session = Depends(get_db)
):
    total = db.query(Customer).count()
    offset = (page - 1) * limit
    customers = db.query(Customer).offset(offset).limit(limit).all()

    return {
        "data": customers,
        "total": total,
        "page": page,
        "limit": limit
    }

@app.get("/api/customers/{id}")
def get_customer(id: str, db: Session = Depends(get_db)):
    customer = db.query(Customer).filter(Customer.customer_id == id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer