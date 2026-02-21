import sys
import os
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from utils.fetch import fetch_data
from utils.recommend import recommend_inheritance

# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

root = tk.Tk()
root.title("Uma Musume Helper")
root.geometry("900x600")

horses_data = []
cards_data = []
current_image = None

frame = ttk.Frame(root, padding=10)
frame.pack(fill="both", expand=True)

title_label = ttk.Label(frame, text="Uma Musume Helper", font=("Arial", 16))
title_label.pack()

update_button = ttk.Button(frame, text="Update Horses & Cards")
update_button.pack(pady=5)

horse_combo = ttk.Combobox(frame, state="readonly", width=50)
horse_combo.pack(pady=5)

inherit_button = ttk.Button(frame, text="Recommend Inheritance")
inherit_button.pack(pady=5)

image_label = ttk.Label(frame)
image_label.pack(pady=10)

output_text = tk.Text(frame, wrap="word")
output_text.pack(fill="both", expand=True)

def update_data():
    global horses_data, cards_data
    data = fetch_data()
    horses_data = data.get("horses", [])
    cards_data = data.get("cards", [])

    horse_combo["values"] = [h['name'] for h in horses_data]
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, f"Loaded {len(horses_data)} horses.\n")

def show_image(path):
    global current_image
    if path and os.path.exists(path):
        img = Image.open(path)
        img = img.resize((200, 200))
        current_image = ImageTk.PhotoImage(img)
        image_label.config(image=current_image)
    else:
        image_label.config(image="")

def recommend():
    selected = horse_combo.get()
    if not selected:
        messagebox.showwarning("Warning", "Select a horse first.")
        return

    horse = next((h for h in horses_data if h["name"] == selected), None)
    if not horse:
        return

    show_image(horse.get("image"))

    result = recommend_inheritance(selected, horses_data)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)

update_button.config(command=update_data)
inherit_button.config(command=recommend)

root.mainloop()
sys.exit(0)
