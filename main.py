import os
import sys
import threading
import logging
import time
import requests
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageDraw, ImageTk
from io import BytesIO

from utils.fetch import fetch_all_data

# =========================
# PATH + LOGGING
# =========================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
LOG_DIR = os.path.join(BASE_PATH, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# =========================
# IMAGE LOADING
# =========================

IMAGE_SIZE = 150
image_refs = []
image_cache = {}

def load_image_from_url(url, fallback_text):
    try:
        if not url:
            raise Exception("No image URL")

        if url in image_cache:
            return image_cache[url]

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))
        img = img.resize((IMAGE_SIZE, IMAGE_SIZE), Image.LANCZOS)

        tk_img = ImageTk.PhotoImage(img)
        image_cache[url] = tk_img
        return tk_img

    except Exception:
        return create_placeholder_image(fallback_text)


def create_placeholder_image(text):
    img = Image.new("RGB", (IMAGE_SIZE, IMAGE_SIZE), color=(35, 35, 35))
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, 0, IMAGE_SIZE - 1, IMAGE_SIZE - 1), outline=(255, 105, 180), width=3)
    draw.text((20, IMAGE_SIZE // 2 - 10), text[:10], fill=(255, 255, 255))
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
        horses, cards = fetch_all_data()
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

    create_section("HORSES", horses)
    create_section("SUPPORT CARDS", cards)

    status_var.set(f"Loaded {len(horses)} horses and {len(cards)} cards.")
    logging.info("GUI updated successfully")

# =========================
# GRID SECTION BUILDER
# =========================

def create_section(title, items):
    title_label = tk.Label(
        content_frame,
        text=title,
        font=("Segoe UI", 14, "bold"),
        bg="#1e1e1e",
        fg="#ff69b4",
        anchor="w"
    )
    title_label.pack(fill="x", pady=(20, 10), padx=10)

    grid_frame = tk.Frame(content_frame, bg="#1e1e1e")
    grid_frame.pack(padx=10)

    columns = 3

    for index, item in enumerate(items):
        row = index // columns
        col = index % columns

        card = tk.Frame(
            grid_frame,
            bg="#2b2b2b",
            width=170,
            height=220,
            bd=1,
            relief="solid"
        )
        card.grid(row=row, column=col, padx=10, pady=10)
        card.grid_propagate(False)

        img = load_image_from_url(item.get("image"), item["name"])
        image_refs.append(img)

        img_label = tk.Label(card, image=img, bg="#2b2b2b")
        img_label.pack(pady=(15, 10))

        name_label = tk.Label(
            card,
            text=item["name"],
            font=("Segoe UI", 10),
            bg="#2b2b2b",
            fg="white",
            wraplength=150,
            justify="center"
        )
        name_label.pack()

# =========================
# GUI SETUP
# =========================

root = tk.Tk()
root.title("Umamusume Builder")
root.geometry("800x750")
root.configure(bg="#1e1e1e")

header = tk.Label(
    root,
    text="Umamusume Data Builder",
    font=("Segoe UI", 20, "bold"),
    bg="#1e1e1e",
    fg="#ff69b4"
)
header.pack(pady=20)

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
update_button.pack()

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
