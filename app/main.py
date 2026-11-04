
import os
import shutil
import uuid

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database import engine, Base, get_db
from app import models
from app.models import Document

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)


@app.get("/")
def home():
    return {"message": "PrezDocs API is running"}


@app.get("/health/db")
def check_database():
    try:
        from sqlalchemy import text

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
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):

    # 1. Validate file extension
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )

    # 2. Create uploads directory
    os.makedirs("uploads", exist_ok=True)

    # 3. Generate a unique filename
    safe_filename = f"{uuid.uuid4()}.pdf"
    file_path = os.path.join("uploads", safe_filename)

    try:
        # 4. Save the PDF locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 5. Create database record
        new_document = Document(
            filename=file.filename,
            file_path=file_path,
            content_type=file.content_type,
            status="uploaded"
        )

        # 6. Save record to PostgreSQL
        db.add(new_document)
        db.commit()
        db.refresh(new_document)

        # 7. Return response
        return {
            "id": new_document.id,
            "filename": new_document.filename,
            "status": new_document.status,
            "message": "Document uploaded successfully"
        }

    except Exception:
        db.rollback()

        # Remove saved file if database insertion fails
        if os.path.exists(file_path):
            os.remove(file_path)

        raise HTTPException(
            status_code=500,
            detail="Document upload failed"
        )

    finally:
        await file.close()
@app.get("/documents")
def get_documents(db: Session = Depends(get_db)):
      documents = db.query(Document).all()
      return documents

