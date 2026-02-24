import logging
import os
from gui import run

if not os.path.exists("data"):
    os.makedirs("data")

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

run()
