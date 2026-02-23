from pathlib import Path
import logging

# CREATE FOLDERS FIRST
Path("logs").mkdir(parents=True, exist_ok=True)
Path("data/images").mkdir(parents=True, exist_ok=True)

# THEN CONFIGURE LOGGING
logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

from gui import App  # Import AFTER logging setup


if __name__ == "__main__":
    app = App()
    app.mainloop()
