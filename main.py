# main.py

import os
import sys
import logging
from pathlib import Path


def get_base_path():
    """
    Ensures paths work in both normal python and PyInstaller exe.
    """
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).parent
    return Path(__file__).parent


BASE_DIR = get_base_path()
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
IMAGE_HORSE_DIR = DATA_DIR / "images" / "horses"
IMAGE_CARD_DIR = DATA_DIR / "images" / "support"

# Always create folders
LOG_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_HORSE_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_CARD_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

from gui import UmamusumeGUI

if __name__ == "__main__":
    app = UmamusumeGUI(base_path=BASE_DIR)
    app.run()
