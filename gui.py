import json
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from PIL import Image, ImageTk
import logging

from crawler import crawl_all


class App(tk.Tk):

    def __init__(self, base_dir: Path):
        super().__init__()

        self.base_dir = base_dir
        self.data_file = base_dir / "data" / "data.json"

        self.title("Umamusume Builder")
        self.geometry("1000x700")

        self.images_cache = []

        self.create_widgets()
        self.ensure_data_file()

    def create_widgets(self):

        top = tk.Frame(self)
        top.pack(pady=10)

        self.crawl_btn = tk.Button(top, text="Crawl Wiki", command=self.start_crawl)
        self.crawl_btn.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(self, length=400)
        self.progress.pack(pady=5)

        self.status_label = tk.Label(self, text="Idle")
        self.status_label.pack()

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar.pack(side="right", fill="y")

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def ensure_data_file(self):
        if not self.data_file.exists():
            self.data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.data_file, "w") as f:
                json.dump({"horses": [], "cards": []}, f)

    def start_crawl(self):
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        logging.info("Starting crawl")
        data = crawl_all(self.base_dir, self.update_progress)

        with open(self.data_file, "w") as f:
            json.dump(data, f, indent=2)

        self.display_images(data)

        self.update_progress(100, "Finished")

    def update_progress(self, percent, message):
        self.progress["value"] = percent
        self.status_label.config(text=message)
        self.update_idletasks()

    def display_images(self, data):
        for w in self.frame.winfo_children():
            w.destroy()

        self.images_cache.clear()

        items = data["horses"][:10] + data["cards"][:10]

        for item in items:
            img_path = Path(item["image"])
            if not img_path.exists():
                continue

            img = Image.open(img_path)
            img = img.resize((120, 120))
            photo = ImageTk.PhotoImage(img)

            lbl = tk.Label(self.frame, image=photo, text=item["name"], compound="top")
            lbl.image = photo
            lbl.pack(side="left", padx=10, pady=10)

            self.images_cache.append(photo)
