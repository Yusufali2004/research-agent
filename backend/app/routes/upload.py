from fastapi import APIRouter, UploadFile, File, HTTPException
from app.agents.parser import parse_file
import shutil
import os

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

@router.post("/content")
async def upload_content(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT allowed")

    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = parse_file(file_path)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "uploaded and parsed successfully",
        "extracted_text": extracted_text[:500]  # preview first 500 chars
    }

@router.post("/template")
async def upload_template(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT allowed")

    file_path = f"{UPLOAD_DIR}/template_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = parse_file(file_path)

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "status": "template uploaded and parsed successfully",
        "extracted_text": extracted_text[:500]
    }