import json
import os


DATA_FILE = "data.json"
IMAGE_FOLDER = "data/images/support"


class DataManager:

    def __init__(self):
        self.ensure_folders()

    def ensure_folders(self):
        os.makedirs(IMAGE_FOLDER, exist_ok=True)

    def save(self, horses, supports):
        self.ensure_folders()
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"horses": horses, "supports": supports},
                f,
                indent=2
            )

    def load(self):
        self.ensure_folders()

        if not os.path.exists(DATA_FILE):
            return [], []

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("horses", []), data.get("supports", [])
