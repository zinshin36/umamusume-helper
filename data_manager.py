import json
import os

DATA_FILE = "data.json"


class DataManager:

    def save(self, horses, supports):

        os.makedirs("data/images/support", exist_ok=True)
        os.makedirs("data/images/horse", exist_ok=True)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "horses": horses,
                "supports": supports
            }, f, indent=2)

    def load(self):

        if not os.path.exists(DATA_FILE):
            return [], []

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data.get("horses", []), data.get("supports", [])
