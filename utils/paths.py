import os
import sys

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()

LOG_DIR = os.path.join(BASE_PATH, "logs")
DATA_DIR = os.path.join(BASE_PATH, "data")

os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)
