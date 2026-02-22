import os
import sys
import threading
import logging
import time
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageFont, ImageTk

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
# IMAGE GENERATION
# =========================

def create_placeholder_image(text):
    img = Image.new("RGB", (140, 140), color=(30, 30, 30))
    draw = ImageDraw.Draw(img)

    draw.rectangle((0, 0, 139, 139), outline=(255, 105, 180), width=3)

    draw.text((20, 55), text[:12], fill=(255, 255, 255))

    return ImageTk.PhotoImage(img)

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

    for widget in content_frame.winfo_children():
        widget.destroy()

    image_refs.clear()

    section_label("HORSES")

    for horse in horses:
        add_card(horse)

    section_label("SUPPORT CARDS")

    for card in cards:
        add_card(card)

    status_var.set(f"Loaded {len(horses)} horses and {len(cards)} cards.")

# =========================
# GUI HELPERS
# =========================

image_refs = []

def section_label(text):
    lbl = tk.Label(
        content_frame,
        text=text,
        font=("Segoe UI", 14, "bold"),
        bg="#1e1e1e",
        fg="white",
        anchor="w"
    )
    lbl.pack(fill="x", pady=(15, 5))

def add_card(name):
    card = tk.Frame(content_frame, bg="#2b2b2b", bd=1, relief="solid")
    card.pack(fill="x", pady=5, padx=10)

    img = create_placeholder_image(name)
    image_refs.append(img)

    img_label = tk.Label(card, image=img, bg="#2b2b2b")
    img_label.pack(side="left", padx=10, pady=10)

    name_label = tk.Label(
        card,
        text=name,
        font=("Segoe UI", 12),
        bg="#2b2b2b",
        fg="white"
    )
    name_label.pack(side="left", padx=10)

# =========================
# GUI SETUP
# =========================

root = tk.Tk()
root.title("Umamusume Builder")
root.geometry("600x600")
root.configure(bg="#1e1e1e")

header = tk.Label(
    root,
    text="Umamusume Data Builder",
    font=("Segoe UI", 18, "bold"),
    bg="#1e1e1e",
    fg="#ff69b4"
)
header.pack(pady=15)

update_button = tk.Button(
    root,
    text="Update Data",
    font=("Segoe UI", 12),
    width=20,
    command=start_update,
    bg="#ff69b4",
    fg="white",
    activebackground="#ff85c1"
)
update_button.pack(pady=5)

progress = ttk.Progressbar(
    root,
    mode="indeterminate",
    length=300
)
progress.pack(pady=10)

canvas = tk.Canvas(root, bg="#1e1e1e", highlightthickness=0)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)

content_frame = tk.Frame(canvas, bg="#1e1e1e")

content_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

canvas.create_window((0, 0), window=content_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

status_var = tk.StringVar(value="Idle")

status_label = tk.Label(
    root,
    textvariable=status_var,
    bg="#2b2b2b",
    fg="white",
    anchor="w"
)
status_label.pack(fill="x")

root.mainloop()
