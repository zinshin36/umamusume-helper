import logging
import os
from utils.paths import LOG_DIR

log_file = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger("uma")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_file, encoding="utf-8")
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
