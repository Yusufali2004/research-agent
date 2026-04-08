from fastapi import APIRouter, UploadFile, File, HTTPException
import shutil
import os

router = APIRouter(prefix="/upload", tags=["upload"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_DOC_TYPES = [
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain"
]

ALLOWED_IMG_TYPES = ["image/jpeg", "image/png", "image/jpg"]

@router.post("/content")
async def upload_content(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_DOC_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, TXT allowed for content")
        
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"filename": file.filename, "status": "uploaded successfully"}

# --- NEW: Image Upload Route ---
@router.post("/image")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED_IMG_TYPES:
        raise HTTPException(status_code=400, detail="Only JPG and PNG allowed for images")
        
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    return {"filename": file.filename, "status": "image uploaded successfully"}