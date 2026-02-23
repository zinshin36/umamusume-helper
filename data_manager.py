import os
import json
from datetime import datetime

DATA_FOLDER = "data"
IMAGE_FOLDER = os.path.join(DATA_FOLDER, "images")
DATA_FILE = os.path.join(DATA_FOLDER, "data.json")

def ensure_directories():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(IMAGE_FOLDER, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "horses": [],
                "cards": [],
                "blacklist": [],
                "last_updated": None
            }, f, indent=2)

def load_data():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
