# gui.py

import json
import threading
import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from utils.fetch import fetch_all_sites


class UmamusumeGUI:
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.data_file = base_path / "data" / "data.json"
        self.image_dir = base_path / "data" / "images"

        self.root = tk.Tk()
        self.root.title("Umamusume Builder")
        self.root.geometry("900x600")

        self.create_widgets()
        self.ensure_data_file()

    def create_widgets(self):
        # Top buttons frame
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        self.crawl_btn = tk.Button(top_frame, text="Crawl Sites", command=self.start_crawl)
        self.crawl_btn.pack(side=tk.LEFT, padx=5)

        self.recommend_btn = tk.Button(top_frame, text="Recommend Support Cards")
        self.recommend_btn.pack(side=tk.LEFT, padx=5)

        self.blacklist_btn = tk.Button(top_frame, text="Blacklist Card")
        self.blacklist_btn.pack(side=tk.LEFT, padx=5)

        self.update_btn = tk.Button(top_frame, text="Update Database", command=self.start_crawl)
        self.update_btn.pack(side=tk.LEFT, padx=5)

        # Progress bar
        self.progress = ttk.Progressbar(self.root, length=400, mode="determinate")
        self.progress.pack(pady=10)

        self.status_label = tk.Label(self.root, text="Idle")
        self.status_label.pack()

        # Counts
        self.count_label = tk.Label(self.root, text="Horses: 0 | Cards: 0")
        self.count_label.pack(pady=5)

        # Image display frame
        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)

        self.image_labels = []

    def ensure_data_file(self):
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump({
                    "horses": [],
                    "cards": [],
                    "blacklist": [],
                    "last_updated": ""
                }, f)

    def start_crawl(self):
        self.crawl_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        logging.info("Starting crawl")
        self.set_status("Crawling...")

        data = fetch_all_sites(self.base_path, self.update_progress)

        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

        self.update_counts(data)
        self.display_images()

        self.set_status("Crawl Complete")
        self.crawl_btn.config(state=tk.NORMAL)

    def update_progress(self, percent, message):
        self.progress["value"] = percent
        self.set_status(message)

    def set_status(self, text):
        self.status_label.config(text=text)
        self.root.update_idletasks()

    def update_counts(self, data):
        horses = len(data.get("horses", []))
        cards = len(data.get("cards", []))
        self.count_label.config(text=f"Horses: {horses} | Cards: {cards}")

    def display_images(self):
        for label in self.image_labels:
            label.destroy()
        self.image_labels.clear()

        horse_dir = self.image_dir / "horses"
        card_dir = self.image_dir / "support"

        images = list(horse_dir.glob("*.png"))[:3] + list(card_dir.glob("*.png"))[:3]

        for img_path in images:
            img = Image.open(img_path)
            img = img.resize((120, 120))
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(self.image_frame, image=photo)
            lbl.image = photo
            lbl.pack(side=tk.LEFT, padx=5)

            self.image_labels.append(lbl)

    def run(self):
        self.root.mainloop()
