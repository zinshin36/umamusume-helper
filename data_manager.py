import os
import json
from datetime import datetime

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "data")
HORSE_IMG_DIR = os.path.join(DATA_DIR, "images", "horses")
SUPPORT_IMG_DIR = os.path.join(DATA_DIR, "images", "support")

DATA_FILE = os.path.join(DATA_DIR, "data.json")


def ensure_directories():
    os.makedirs(HORSE_IMG_DIR, exist_ok=True)
    os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)

    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "horses": [],
                "cards": [],
                "blacklist": [],
                "last_updated": None
            }, f, indent=2)


def load_data():
    ensure_directories()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    data["last_updated"] = datetime.now().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
