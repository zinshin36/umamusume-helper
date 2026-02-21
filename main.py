import sys
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from utils.fetch import fetch_data
from utils.recommend import recommend_inheritance

# ----------------------------
# Logging Setup
# ----------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Application started")

# ----------------------------
# GUI Setup (Tkinter)
# ----------------------------
root = tk.Tk()
root.title("Uma Musume Helper")
root.geometry("800x500")

horses_data = []
cards_data = []

# Frame
frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

title_label = ttk.Label(frame, text="Uma Musume Helper (EN Wiki)", font=("Arial", 16))
title_label.pack(pady=10)

update_button = ttk.Button(frame, text="Update Horses & Cards")
update_button.pack(pady=5)

horse_label = ttk.Label(frame, text="Select Horse:")
horse_label.pack(pady=5)

horse_combo = ttk.Combobox(frame, state="readonly", width=50)
horse_combo.pack(pady=5)

inherit_button = ttk.Button(frame, text="Recommend Inheritance")
inherit_button.pack(pady=5)

output_text = tk.Text(frame, wrap="word")
output_text.pack(fill="both", expand=True, pady=10)

def update_data():
    global horses_data, cards_data
    data = fetch_data()
    horses_data = data.get("horses", [])
    cards_data = data.get("cards", [])

    horse_names = [h['name'] for h in horses_data]
    horse_combo["values"] = horse_names

    logging.info(f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.")
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.\n")

def recommend():
    selected = horse_combo.get()
    if not selected:
        messagebox.showwarning("Warning", "Please select a horse first.")
        return

    result = recommend_inheritance(selected, horses_data)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

update_button.config(command=update_data)
inherit_button.config(command=recommend)

root.mainloop()

logging.info("Application closed")
sys.exit(0)
