# gui.py

import json
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk

from crawler import crawl_all


class UmamusumeGUI:

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.data_file = base_path / "data" / "data.json"

        self.root = tk.Tk()
        self.root.title("Umamusume Builder")
        self.root.geometry("900x600")

        self.create_widgets()
        self.ensure_data_file()

    def create_widgets(self):
        top = tk.Frame(self.root)
        top.pack(pady=10)

        self.crawl_btn = tk.Button(top, text="Crawl Wiki", command=self.start_crawl)
        self.crawl_btn.pack(side=tk.LEFT, padx=5)

        self.progress = ttk.Progressbar(self.root, length=400)
        self.progress.pack(pady=5)

        self.status = tk.Label(self.root, text="Idle")
        self.status.pack()

        self.count_label = tk.Label(self.root, text="Horses: 0 | Cards: 0")
        self.count_label.pack(pady=5)

        self.image_frame = tk.Frame(self.root)
        self.image_frame.pack(pady=10)

        self.image_labels = []

    def ensure_data_file(self):
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump({"horses": [], "cards": [], "blacklist": []}, f)

    def start_crawl(self):
        self.crawl_btn.config(state=tk.DISABLED)
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        data = crawl_all(self.base_path, self.update_progress)

        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

        self.update_counts(data)
        self.display_images()

        self.status.config(text="Finished")
        self.crawl_btn.config(state=tk.NORMAL)

    def update_progress(self, percent, message):
        self.progress["value"] = percent
        self.status.config(text=message)
        self.root.update_idletasks()

    def update_counts(self, data):
        self.count_label.config(
            text=f"Horses: {len(data['horses'])} | Cards: {len(data['cards'])}"
        )

    def display_images(self):
        for lbl in self.image_labels:
            lbl.destroy()
        self.image_labels.clear()

        horse_dir = self.base_path / "data" / "images" / "horses"
        card_dir = self.base_path / "data" / "images" / "support"

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
