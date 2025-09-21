from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import json
import os
from datetime import datetime


app = FastAPI(title="Test API")


IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
IMG_DIR = os.path.normpath(IMG_DIR)
os.makedirs(IMG_DIR, exist_ok=True)

METADATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata")
METADATA_DIR = os.path.normpath(METADATA_DIR)
os.makedirs(METADATA_DIR, exist_ok=True)


@app.post("/send_photo")
async def send_photo(
    photo: UploadFile = File(..., description="Файл изображения"),
    metadata: str = Form(..., description="JSON-массив с метаданными"),
):
    try:
        # Разбор JSON-строки в массив/объект
        parsed_metadata = json.loads(metadata)
    except json.JSONDecodeError:
        return JSONResponse(status_code=400, content={"detail": "Некорректный JSON в поле metadata"})

    # Логируем метаданные в консоль
    print("[send_photo] metadata:", json.dumps(parsed_metadata, ensure_ascii=False, indent=2))

    # Формируем имя файла
    original_name = os.path.basename(photo.filename or "uploaded")
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    safe_name = f"{name}_{timestamp}{ext or '.bin'}"
    save_path = os.path.join(IMG_DIR, safe_name)

    # Сохраняем файл на диск
    with open(save_path, "wb") as f:
        f.write(await photo.read())
    
    # Сохраняем метаданные в JSON
    base_name = os.path.splitext(safe_name)[0]
    metadata_path = os.path.join(METADATA_DIR, f"{base_name}.json")
    with open(metadata_path, "w", encoding="utf-8") as mf:
        json.dump(parsed_metadata, mf, ensure_ascii=False, indent=2)

    return {"status": "ok", "saved_as": safe_name, "metadata_saved_as": f"{base_name}.json"}


@app.get("/")
async def root():
    return {"message": "FastAPI backend is running"}


