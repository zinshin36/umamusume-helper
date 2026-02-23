# main.py

import sys
import os
import logging
from pathlib import Path


def get_base_path():
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


BASE_PATH = get_base_path()

DATA_DIR = BASE_PATH / "data"
LOG_DIR = BASE_PATH / "logs"
HORSE_IMG_DIR = DATA_DIR / "images" / "horses"
CARD_IMG_DIR = DATA_DIR / "images" / "support"

# Ensure directories exist
HORSE_IMG_DIR.mkdir(parents=True, exist_ok=True)
CARD_IMG_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

from gui import UmamusumeGUI

if __name__ == "__main__":
    app = UmamusumeGUI(BASE_PATH)
    app.run()
