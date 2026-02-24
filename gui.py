import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import json
import os
import logging

from crawler import crawl

DATA_FILE = "data/data.json"

class App:

    def __init__(self, root):
        self.root = root
        root.title("Uma Planner")

        self.images = {}
        self.selected_card = None

        self.top = ttk.Frame(root)
        self.top.pack(fill="x")

        self.update_btn = ttk.Button(self.top, text="Update Database", command=self.update_db)
        self.update_btn.pack(side="left")

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(self.top, maximum=100, variable=self.progress_var)
        self.progress.pack(fill="x", expand=True, padx=5)

        self.status = ttk.Label(root, text="Ready")
        self.status.pack()

        self.count_label = ttk.Label(root, text="Horses: 0 Cards: 0")
        self.count_label.pack()

        self.canvas = tk.Canvas(root)
        self.scroll = ttk.Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.frame = ttk.Frame(self.canvas)

        self.frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0,0), window=self.frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scroll.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")

        self.load_data()

    def update_progress(self, current, total):
        percent = (current / total) * 100
        self.progress_var.set(percent)
        self.status.config(text=f"{int(percent)}%")

    def update_db(self):
        threading.Thread(target=self.run_crawl).start()

    def run_crawl(self):
        crawl(progress=self.update_progress)
        self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        horses = data["horses"]
        cards = data["cards"]

        self.count_label.config(text=f"Horses: {len(horses)} Cards: {len(cards)}")

        for widget in self.frame.winfo_children():
            widget.destroy()

        row = 0
        col = 0

        for card in cards:

            path = card["image"]
            if not os.path.exists(path):
                continue

            img = Image.open(path).resize((100, 100))
            photo = ImageTk.PhotoImage(img)
            self.images[card["id"]] = photo

            lbl = tk.Label(self.frame, image=photo, borderwidth=2, relief="solid")
            lbl.grid(row=row, column=col, padx=5, pady=5)

            lbl.bind("<Button-1>", lambda e, c=card: self.select_card(c))
            lbl.bind("<Button-3>", lambda e, c=card: self.toggle_blacklist(c))

            col += 1
            if col >= 6:
                col = 0
                row += 1

    def select_card(self, card):
        self.status.config(text=f"Selected: {card['name']}")

    def toggle_blacklist(self, card):
        card["blacklisted"] = not card.get("blacklisted", False)
        self.status.config(text=f"Blacklisted: {card['name']} = {card['blacklisted']}")
        self.save_changes()

    def save_changes(self):
        with open(DATA_FILE, "r+", encoding="utf-8") as f:
            data = json.load(f)
            for c in data["cards"]:
                if c["id"] in self.images:
                    c["blacklisted"] = c.get("blacklisted", False)
            f.seek(0)
            json.dump(data, f, indent=2)
            f.truncate()


root = tk.Tk()
app = App(root)
root.mainloop()
