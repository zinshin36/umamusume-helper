import sys
import logging
from pathlib import Path

# ✅ Detect correct runtime directory (works for .exe and normal python)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).parent.resolve()

DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"

(DATA_DIR / "images" / "horses").mkdir(parents=True, exist_ok=True)
(DATA_DIR / "images" / "support").mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

LOG_FILE = LOG_DIR / "app.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    force=True
)

logging.info("Application started")
logging.info(f"Base directory: {BASE_DIR}")

from gui import App

if __name__ == "__main__":
    app = App(BASE_DIR)
    app.mainloop()
