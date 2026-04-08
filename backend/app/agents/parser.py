import os
import uuid
import pypdf
from docx import Document

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def parse_file(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext == ".txt":
        return parse_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def parse_pdf(file_path: str) -> str:
    text = ""
    with open(file_path, "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            # 1. Grab the text
            text += page.extract_text() or ""
            text += "\n"
            
            # 2. Grab the images! (The MVP Hackathon Trick)
            for image_file_object in page.images:
                # Create a safe, unique filename
                img_filename = f"img_{uuid.uuid4().hex[:6]}.png"
                img_path = os.path.join(UPLOAD_DIR, img_filename)
                
                # Save the extracted image to the backend/uploads folder
                with open(img_path, "wb") as img_out:
                    img_out.write(image_file_object.data)
                    
                # Automatically inject our special tag into the text so the AI sees it
                text += f"\n[IMAGE: {img_filename}]\n"
                
    return text.strip()

def parse_docx(file_path: str) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs if para.text.strip()])

def parse_txt(file_path: str) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read().strip()