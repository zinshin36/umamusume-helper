import sys
import os
import json
import logging
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

from utils.fetch import fetch_horses, fetch_cards
from utils.recommend import find_horse, STAT_PRIORITY

# ----------------------------
# Directories
# ----------------------------
os.makedirs("logs", exist_ok=True)
os.makedirs("data", exist_ok=True)

# ----------------------------
# Logging
# ----------------------------
logging.basicConfig(
    filename="logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# ----------------------------
# Globals
# ----------------------------
horses_data = []
cards_data = []
blacklist = set()

CACHE_FILE = "data/cache.json"
USER_FILE = "data/user_config.json"

# ----------------------------
# Utility Functions
# ----------------------------
def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses_data, "cards": cards_data}, f)

def load_cache():
    global horses_data, cards_data
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            horses_data = data.get("horses", [])
            cards_data = data.get("cards", [])
            logging.info("Loaded data from cache.")

def save_user_config():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump({"blacklist": list(blacklist)}, f)

def load_user_config():
    global blacklist
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            blacklist = set(data.get("blacklist", []))

# ----------------------------
# Data Updating
# ----------------------------
def update_data():
    global horses_data, cards_data

    status_label.config(text="Updating data...")
    root.update()

    horses = fetch_horses()
    cards = fetch_cards()

    if horses and cards:
        horses_data = horses
        cards_data = cards
        save_cache()
        populate_dropdown()
        status_label.config(text="Data updated successfully.")
        logging.info("Data updated successfully.")
    else:
        status_label.config(text="API failed. Using cached data.")
        logging.warning("API failed, using cache.")
        load_cache()
        populate_dropdown()

def populate_dropdown():
    names = sorted(list(set([h["name"] for h in horses_data])))
    horse_dropdown["values"] = names

# ----------------------------
# Recommendation Engine
# ----------------------------
def build_scored_deck(horse):
    priority = STAT_PRIORITY.get(horse.get("type"), [])
    valid_cards = [
        c for c in cards_data
        if c["name"] not in blacklist
    ]

    scored = []
    for card in valid_cards:
        score = 0
        if card.get("type") in priority:
            score += (len(priority) - priority.index(card["type"])) * 10
        score += card.get("rarity", 1) * 2
        scored.append((score, card))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [c[1] for c in scored[:6]]

def generate_recommendation():
    selected = horse_var.get()
    if not selected:
        messagebox.showwarning("No Horse Selected", "Please select a horse.")
        return

    matches = find_horse(selected, horses_data)
    if not matches:
        messagebox.showerror("Not Found", "Horse not found.")
        return

    horse = matches[0]
    deck = build_scored_deck(horse)
    races = horse.get("distances", [])

    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Horse: {horse['name']}\n")
    output_text.insert(tk.END, f"Type: {horse.get('type','Unknown')}\n\n")

    output_text.insert(tk.END, "Recommended Support Deck:\n")
    output_text.insert(tk.END, "-"*40 + "\n")
    for card in deck:
        output_text.insert(tk.END, f"{card['name']} ({card.get('type','?')})\n")

    output_text.insert(tk.END, "\nRecommended Race Distances:\n")
    output_text.insert(tk.END, "-"*40 + "\n")
    for r in races:
        output_text.insert(tk.END, f"{r}\n")

    logging.info(f"Generated recommendation for {horse['name']}")

# ----------------------------
# Blacklist Management
# ----------------------------
def add_to_blacklist():
    card = blacklist_entry.get()
    if card:
        blacklist.add(card)
        save_user_config()
        blacklist_entry.delete(0, tk.END)
        messagebox.showinfo("Blacklist Updated", f"{card} added.")

# ----------------------------
# GUI
# ----------------------------
root = tk.Tk()
root.title("Uma Musume Helper - Global")
root.geometry("1000x700")

title_label = tk.Label(root, text="Uma Musume Helper (Global Server)", font=("Arial", 18))
title_label.pack(pady=10)

top_frame = tk.Frame(root)
top_frame.pack(pady=5)

horse_var = tk.StringVar()
horse_dropdown = ttk.Combobox(top_frame, textvariable=horse_var, width=40)
horse_dropdown.pack(side=tk.LEFT, padx=5)

recommend_button = tk.Button(top_frame, text="Recommend", command=generate_recommendation)
recommend_button.pack(side=tk.LEFT, padx=5)

update_button = tk.Button(top_frame, text="Update Data", command=update_data)
update_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(top_frame, text="Exit", command=root.destroy)
exit_button.pack(side=tk.LEFT, padx=5)

blacklist_frame = tk.Frame(root)
blacklist_frame.pack(pady=5)

blacklist_entry = tk.Entry(blacklist_frame, width=40)
blacklist_entry.pack(side=tk.LEFT, padx=5)

blacklist_button = tk.Button(blacklist_frame, text="Add to Blacklist", command=add_to_blacklist)
blacklist_button.pack(side=tk.LEFT)

output_text = scrolledtext.ScrolledText(root, width=120, height=30)
output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

status_label = tk.Label(root, text="Loading data...")
status_label.pack(pady=5)

# Load config + auto update
load_user_config()
load_cache()
populate_dropdown()
update_data()

root.mainloop()

logging.info("Application closed")
sys.exit(0)
