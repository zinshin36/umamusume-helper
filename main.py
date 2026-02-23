import logging
import os
from gui import UmaGui
from data_manager import ensure_directories

def setup_logging():
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        filename="logs/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

if __name__ == "__main__":
    ensure_directories()
    setup_logging()

    logging.info("Application started")

    app = UmaGui()
    app.run()
