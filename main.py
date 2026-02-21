import sys
import os
import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.fetch import fetch_data
from utils.recommend import recommend_inheritance

# ----------------------------
# Fix logging path for EXE
# ----------------------------
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(__file__)

log_dir = os.path.join(base_path, "logs")
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "log.txt"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# ----------------------------
# GUI Setup
# ----------------------------
root = tk.Tk()
root.title("Uma Musume Helper")
root.geometry("900x650")

horses_data = []
cards_data = []
horse_images = {}

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

title = ttk.Label(frame, text="Uma Musume Helper", font=("Arial", 18))
title.pack(pady=10)

update_btn = ttk.Button(frame, text="Update Horses & Cards")
update_btn.pack(pady=5)

progress = ttk.Progressbar(frame, orient="horizontal", mode="determinate", length=400)
progress.pack(pady=5)

horse_combo = ttk.Combobox(frame, state="readonly", width=60)
horse_combo.pack(pady=10)

img_label = ttk.Label(frame)
img_label.pack(pady=10)

output = tk.Text(frame, height=10)
output.pack(fill="both", expand=True)

# ----------------------------
# Update Thread
# ----------------------------
def update_data_thread():
    global horses_data, cards_data, horse_images

    progress["value"] = 0
    output.delete("1.0", tk.END)
    output.insert(tk.END, "Starting update...\n")

    data = fetch_data(progress_callback=update_progress)

    horses_data = data.get("horses", [])
    cards_data = data.get("cards", [])

    horse_combo["values"] = [h["name"] for h in horses_data]

    output.insert(tk.END, f"\nLoaded {len(horses_data)} horses\n")
    output.insert(tk.END, f"Loaded {len(cards_data)} support cards\n")

    logging.info(f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.")

def update_progress(value):
    progress["value"] = value
    root.update_idletasks()

def update_data():
    threading.Thread(target=update_data_thread, daemon=True).start()

update_btn.config(command=update_data)

# ----------------------------
# Image Display
# ----------------------------
def show_selected(event):
    selected = horse_combo.get()
    for horse in horses_data:
        if horse["name"] == selected:
            try:
                img = Image.open(horse["image_path"])
                img = img.resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                img_label.config(image=photo)
                img_label.image = photo
            except Exception as e:
                logging.error(str(e))
            break

horse_combo.bind("<<ComboboxSelected>>", show_selected)

root.mainloop()
logging.info("Application closed")
