import json
import os

DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data.json")
STATE_FILE = os.path.join(DATA_DIR, "user_state.json")


def ensure_data_exists(crawl_func):
    if not os.path.exists(DATA_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        crawl_func()


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"horses": [], "cards": []}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"blacklist": [], "stars": {}}
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def toggle_blacklist(card_id):
    state = load_state()
    if card_id in state["blacklist"]:
        state["blacklist"].remove(card_id)
    else:
        state["blacklist"].append(card_id)
    save_state(state)


def set_stars(card_id, stars):
    state = load_state()
    state["stars"][str(card_id)] = stars
    save_state(state)
