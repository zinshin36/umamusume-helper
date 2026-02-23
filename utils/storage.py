import os
import json
from datetime import datetime

DATA_DIR = "data"
IMAGE_DIR = os.path.join(DATA_DIR, "images")
HORSE_IMG_DIR = os.path.join(IMAGE_DIR, "horses")
SUPPORT_IMG_DIR = os.path.join(IMAGE_DIR, "support")

DATA_FILE = os.path.join(DATA_DIR, "data.json")


def ensure_directories():
    os.makedirs(HORSE_IMG_DIR, exist_ok=True)
    os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "horses": [],
            "cards": [],
            "blacklist": [],
            "last_updated": None
        }

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    data["last_updated"] = datetime.now().isoformat()

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def deduplicate(entries):
    seen = set()
    result = []

    for item in entries:
        name = item["name"].strip()
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        result.append(item)

    return result
