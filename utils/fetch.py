import json
from pathlib import Path

from data_sources.umamusumedb import fetch_all as fetch_umadb

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "data.json"

DATA_DIR.mkdir(exist_ok=True)
(DATA_DIR / "images").mkdir(exist_ok=True)


def fetch_all_sites(progress_callback=None):

    horses = []
    cards = []

    # --- UMAMUSUMEDB ---
    h, c = fetch_umadb(progress_callback)
    horses.extend(h)
    cards.extend(c)

    # Remove duplicates
    horses = {h["name"]: h for h in horses}.values()
    cards = {c["name"]: c for c in cards}.values()

    data = {
        "horses": list(horses),
        "cards": list(cards),
        "blacklist": [],
        "last_updated": None
    }

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return len(data["horses"]), len(data["cards"])
