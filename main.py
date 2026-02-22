import os
import sys
import threading
import logging
import time
import tkinter as tk
from tkinter import messagebox

# =========================
# PATH + LOGGING SETUP
# =========================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
LOG_DIR = os.path.join(BASE_PATH, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# =========================
# SIMULATED DATA FETCH
# =========================

def fetch_data():
    logging.info("Fetching data...")
    time.sleep(2)

    horses = ["Special Week", "Silence Suzuka", "Tokai Teio"]
    cards = ["Kitasan Black", "Fine Motion", "Super Creek"]

    logging.info("Fetch complete")
    return horses, cards

# =========================
# THREAD HANDLER
# =========================

def start_update():
    status_label.config(text="Status: Fetching data...")
    threading.Thread(target=update_thread, daemon=True).start()

def update_thread():
    try:
        horses, cards = fetch_data()
        root.after(0, lambda: status_label.config(
            text=f"Loaded {len(horses)} horses and {len(cards)} cards."
        ))
    except Exception as e:
        logging.error(str(e))
        root.after(0, lambda: messagebox.showerror("Error", str(e)))

# =========================
# GUI
# =========================

root = tk.Tk()
root.title("Umamusume Builder")
root.geometry("350x150")

update_button = tk.Button(root, text="Update Data", command=start_update)
update_button.pack(pady=20)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack()

root.mainloop()
