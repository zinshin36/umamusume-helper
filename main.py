import logging
from gui import start_app

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

if __name__ == "__main__":
    start_app()
