import os
import json
import logging
from datetime import datetime

BASE_DIR = os.getcwd()

DATA_DIR = os.path.join(BASE_DIR, "data")
IMAGE_DIR = os.path.join(DATA_DIR, "images")
HORSE_IMG_DIR = os.path.join(IMAGE_DIR, "horses")
SUPPORT_IMG_DIR = os.path.join(IMAGE_DIR, "support")
LOG_DIR = os.path.join(BASE_DIR, "logs")

DATA_FILE = os.path.join(DATA_DIR, "data.json")
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def ensure_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(HORSE_IMG_DIR, exist_ok=True)
    os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)


def setup_logging():
    ensure_directories()

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    logging.info("Application started")


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
