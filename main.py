import os
import sys
import threading
import logging
import time
import tkinter as tk
from tkinter import ttk, messagebox

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
# UPDATE THREAD
# =========================

def start_update():
    progress.start()
    status_var.set("Fetching data...")
    update_button.config(state="disabled")
    threading.Thread(target=update_thread, daemon=True).start()

def update_thread():
    try:
        horses, cards = fetch_data()

        root.after(0, lambda: finish_update(horses, cards))

    except Exception as e:
        logging.error(str(e))
        root.after(0, lambda: messagebox.showerror("Error", str(e)))

def finish_update(horses, cards):
    progress.stop()
    update_button.config(state="normal")

    results_box.delete("1.0", tk.END)
    results_box.insert(tk.END, "=== HORSES ===\n")
    for h in horses:
        results_box.insert(tk.END, f"- {h}\n")

    results_box.insert(tk.END, "\n=== SUPPORT CARDS ===\n")
    for c in cards:
        results_box.insert(tk.END, f"- {c}\n")

    status_var.set(f"Loaded {len(horses)} horses and {len(cards)} cards.")

# =========================
# GUI SETUP
# =========================

root = tk.Tk()
root.title("Umamusume Builder")
root.geometry("500x400")
root.resizable(False, False)

header = tk.Label(
    root,
    text="Umamusume Data Builder",
    font=("Segoe UI", 16, "bold")
)
header.pack(pady=10)

update_button = tk.Button(
    root,
    text="Update Data",
    width=20,
    height=2,
    command=start_update
)
update_button.pack(pady=5)

progress = ttk.Progressbar(
    root,
    mode="indeterminate",
    length=300
)
progress.pack(pady=5)

results_frame = tk.Frame(root)
results_frame.pack(pady=10, fill="both", expand=True)

scrollbar = tk.Scrollbar(results_frame)
scrollbar.pack(side="right", fill="y")

results_box = tk.Text(
    results_frame,
    height=12,
    width=60,
    yscrollcommand=scrollbar.set
)
results_box.pack(side="left", fill="both", expand=True)

scrollbar.config(command=results_box.yview)

status_var = tk.StringVar()
status_var.set("Idle")

status_label = tk.Label(
    root,
    textvariable=status_var,
    relief="sunken",
    anchor="w"
)
status_label.pack(fill="x", side="bottom")

root.mainloop()
