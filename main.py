import logging
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("Application started")

from gui import start_app

if __name__ == "__main__":
    start_app()
