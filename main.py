from pathlib import Path
import logging

from gui import App

Path("data/images").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename="logs/app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

if __name__ == "__main__":
    app = App()
    app.mainloop()
