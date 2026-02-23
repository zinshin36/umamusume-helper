import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import json
import os
from datetime import datetime

from utils.fetch import fetch_all_sites

DATA_FILE = "data/data.json"


class App(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Uma Manager")
        self.geometry("1200x800")

        self.horses = []
        self.cards = []
        self.blacklist = []

        self.create_widgets()
        self.load_data()

    # ================= UI =================

    def create_widgets(self):

        top = tk.Frame(self)
        top.pack(fill="x")

        self.progress = ttk.Progressbar(top, length=200)
        self.progress.pack(side="left", padx=10)

        self.status_label = tk.Label(top, text="Ready")
        self.status_label.pack(side="left", padx=10)

        tk.Button(top, text="Crawl", command=self.start_crawl).pack(side="right", padx=5)
        tk.Button(top, text="Recommend Cards", command=self.recommend_cards).pack(side="right", padx=5)
        tk.Button(top, text="Check Updates", command=self.check_updates).pack(side="right", padx=5)

        self.horse_label = tk.Label(top, text="Horses: 0")
        self.horse_label.pack(side="left", padx=10)

        self.card_label = tk.Label(top, text="Support Cards: 0")
        self.card_label.pack(side="left", padx=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    # ================= DATA =================

    def load_data(self):

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.horses = data.get("horses", [])
        self.cards = data.get("cards", [])
        self.blacklist = data.get("blacklist", [])

        self.horse_label.config(text=f"Horses: {len(self.horses)}")
        self.card_label.config(text=f"Support Cards: {len(self.cards)}")

        self.display_items(self.horses)

    # ================= CRAWL =================

    def start_crawl(self):

        self.progress["value"] = 0
        self.status_label.config(text="Crawling...")

        def progress_callback(text):
            percent = int(text.split("%")[0].split()[-1])
            self.progress["value"] = percent
            self.status_label.config(text=text)
            self.update_idletasks()

        horses, cards = fetch_all_sites(progress_callback)

        self.status_label.config(text="Crawl Complete")
        self.progress["value"] = 100

        self.load_data()

        messagebox.showinfo("Done", f"{horses} horses\n{cards} cards")

    # ================= DISPLAY =================

    def display_items(self, items):

        for w in self.scroll_frame.winfo_children():
            w.destroy()

        self.images = []
        cols = 5
        row = 0
        col = 0

        for item in items:

            if not item.get("image"):
                continue

            try:
                img = Image.open(item["image"])
                img = img.resize((150, 200))
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)

                frame = tk.Frame(self.scroll_frame)
                frame.grid(row=row, column=col, padx=10, pady=10)

                tk.Label(frame, image=photo).pack()
                tk.Label(frame, text=item["name"], wraplength=150).pack()

                col += 1
                if col >= cols:
                    col = 0
                    row += 1

            except:
                continue

    # ================= RECOMMEND =================

    def recommend_cards(self):

        filtered = [c for c in self.cards if c["name"] not in self.blacklist]
        self.display_items(filtered)

    # ================= UPDATE CHECK =================

    def check_updates(self):

        self.status_label.config(text="Checking for updates...")
        self.update_idletasks()

        # Simple: just re-crawl and compare count
        old_count = len(self.cards)
        horses, cards = fetch_all_sites()

        if cards > old_count:
            messagebox.showinfo("Update Found", "New support cards detected!")
        else:
            messagebox.showinfo("No Updates", "No new cards found.")

        self.load_data()
