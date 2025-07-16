import os
from fastapi import UploadFile
from uuid import uuid4

UPLOAD_DIR = "static/uploads"

def save_image(file: UploadFile) -> str:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    filename = f"{uuid4().hex}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return f"/uploads/{filename}"  # serve this via StaticFiles in FastAPI
