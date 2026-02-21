import os
import json
import threading
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.fetch import fetch_all
from utils.recommend import recommend_inheritance

DATA_DIR = "data"
IMAGE_DIR = "images"
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(IMAGE_DIR, exist_ok=True)

characters = []
support_cards = []

root = tk.Tk()
root.title("Uma Musume Deck Builder")
root.geometry("1000x750")

progress = ttk.Progressbar(root, length=500)
progress.pack(pady=5)

update_button = ttk.Button(root, text="Update Data")
update_button.pack(pady=5)

notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True)

tab_main = ttk.Frame(notebook)
notebook.add(tab_main, text="Characters")

tab_support = ttk.Frame(notebook)
notebook.add(tab_support, text="Support Cards")

char_combo = ttk.Combobox(tab_main, width=60)
char_combo.pack(pady=10)

char_image_label = ttk.Label(tab_main)
char_image_label.pack()

output = tk.Text(tab_main, height=8)
output.pack(fill="x")

def update_progress(val):
    progress["value"] = val
    root.update_idletasks()

def update_data():
    global characters, support_cards

    characters, support_cards = fetch_all(update_progress)

    with open(os.path.join(DATA_DIR, "characters.json"), "w", encoding="utf-8") as f:
        json.dump(characters, f, indent=2, ensure_ascii=False)

    with open(os.path.join(DATA_DIR, "support_cards.json"), "w", encoding="utf-8") as f:
        json.dump(support_cards, f, indent=2, ensure_ascii=False)

    char_combo["values"] = [c["name"] for c in characters]

def update_thread():
    threading.Thread(target=update_data, daemon=True).start()

update_button.config(command=update_thread)

def on_select(event):
    selected = char_combo.get()
    for c in characters:
        if c["name"] == selected:
            if c["images"]:
                try:
                    img = Image.open(c["images"][0])
                    img = img.resize((250, 250))
                    photo = ImageTk.PhotoImage(img)
                    char_image_label.config(image=photo)
                    char_image_label.image = photo
                except:
                    pass

            rec = recommend_inheritance(c)
            output.delete("1.0", tk.END)
            output.insert(tk.END, json.dumps(rec, indent=2))
            break

char_combo.bind("<<ComboboxSelected>>", on_select)

root.mainloop()
