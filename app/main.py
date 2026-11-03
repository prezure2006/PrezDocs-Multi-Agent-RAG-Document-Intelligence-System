from sqlalchemy import text
from fastapi import HTTPException
from app.database import engine
from app.database import engine, Base
from app import models

Base.metadata.create_all(bind=engine)

from fastapi import FastAPI, UploadFile, File, HTTPException
app = FastAPI(
    title="PrezDocs API",
    description="Multi-Agent Document Intelligence System",
    version="1.0.0"
)
@app.get("/")
def home():
  return { "message": "Welcome Home son"}

@app.get("/about")
def about():
    return {
        "name": "Prasheel",
        "goal": "AI Engineering",
        "framework": "FastAPI"
    }
@app.get("/health/db")
def check_database():

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        return {
            "database": "connected",
            "status": "healthy"
        }

    except Exception:
        raise HTTPException(
            status_code=503,
            detail="Database connection failed"
        )
@app.post("/uploads/document")
async def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Document received successfully"
    }
