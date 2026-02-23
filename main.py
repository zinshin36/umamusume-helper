import os
from pathlib import Path
import logging

from utils.fetch import fetch_all_sites
from gui import App

# Create folders
Path("data/images").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)

# Logging
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

if __name__ == "__main__":
    app = App()
    app.mainloop()
