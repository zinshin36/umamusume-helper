import json
import os

STATE_FILE = "data/user_state.json"


def load_state():
    if not os.path.exists(STATE_FILE):
        return {"blacklist": [], "stars": {}}
    with open(STATE_FILE, "r") as f:
        return json.load(f)


def save_state(state):
    with open(STATE_FILE, "w") as f:
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
