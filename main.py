from flask import Flask, request, jsonify
from typing import Optional
import json
import os
from datetime import datetime


app = Flask(__name__)


IMG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
IMG_DIR = os.path.normpath(IMG_DIR)
os.makedirs(IMG_DIR, exist_ok=True)

METADATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "metadata")
METADATA_DIR = os.path.normpath(METADATA_DIR)
os.makedirs(METADATA_DIR, exist_ok=True)


@app.route("/send_photo", methods=["POST"])
def send_photo():
    photo = request.files.get("photo")
    metadata_raw = request.form.get("metadata")

    if photo is None or metadata_raw is None:
        return jsonify({"detail": "Поля 'photo' и 'metadata' обязательны"}), 400

    try:
        parsed_metadata = json.loads(metadata_raw)
    except json.JSONDecodeError:
        return jsonify({"detail": "Некорректный JSON в поле metadata"}), 400

    print("[send_photo] metadata:", json.dumps(parsed_metadata, ensure_ascii=False, indent=2))

    original_name = os.path.basename(photo.filename or "uploaded")
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%S%fZ")
    safe_name = f"{name}_{timestamp}{ext or '.bin'}"
    save_path = os.path.join(IMG_DIR, safe_name)

    photo.save(save_path)

    base_name = os.path.splitext(safe_name)[0]
    metadata_path = os.path.join(METADATA_DIR, f"{base_name}.json")
    with open(metadata_path, "w", encoding="utf-8") as mf:
        json.dump(parsed_metadata, mf, ensure_ascii=False, indent=2)

    return jsonify({"status": "ok", "saved_as": safe_name, "metadata_saved_as": f"{base_name}.json"})


@app.get("/")
def root():
    return jsonify({"message": "Flask backend is running"})


if __name__ == "__main__":
    port_str = os.getenv("PORT", "8000")
    try:
        port = int(port_str)
    except ValueError:
        port = 8000
    app.run(host="0.0.0.0", port=port, debug=os.getenv("RELOAD", "false").lower() == "true")

