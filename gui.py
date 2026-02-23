import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import json
import threading
import logging

from utils.fetch import fetch_all_sites


DATA_FILE = "data.json"


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Umamusume Builder")
        self.geometry("900x600")

        self.images_cache = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):

        top_frame = tk.Frame(self)
        top_frame.pack(pady=10)

        self.crawl_btn = tk.Button(top_frame, text="Crawl Wiki", command=self.start_crawl)
        self.crawl_btn.pack(side="left", padx=5)

        self.recommend_btn = tk.Button(top_frame, text="Recommend Support Cards", command=self.recommend_cards)
        self.recommend_btn.pack(side="left", padx=5)

        self.blacklist_btn = tk.Button(top_frame, text="Blacklist Card", command=self.blacklist_card)
        self.blacklist_btn.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(self, mode="indeterminate")
        self.progress.pack(fill="x", padx=20, pady=10)

        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill="both", expand=True)

        self.scrollbar = tk.Scrollbar(self.canvas, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.canvas.yview)

    def start_crawl(self):
        threading.Thread(target=self.crawl).start()

    def crawl(self):
        self.progress.start()
        logging.info("Starting crawl")

        data = fetch_all_sites()

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        self.progress.stop()
        self.load_data()

        messagebox.showinfo("Done", "Crawl complete")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        for widget in self.frame.winfo_children():
            widget.destroy()

        self.images_cache.clear()

        horses = data.get("horses", [])

        for item in horses[:50]:  # limit to avoid overload
            path = item.get("image")

            if not os.path.exists(path):
                continue

            img = Image.open(path)
            img = img.resize((100, 100))
            photo = ImageTk.PhotoImage(img)

            self.images_cache.append(photo)

            label = tk.Label(self.frame, image=photo, text=item["name"], compound="top")
            label.pack(side="left", padx=10, pady=10)

    def recommend_cards(self):
        messagebox.showinfo("Info", "Recommendation system coming next update")

    def blacklist_card(self):
        messagebox.showinfo("Info", "Blacklist system coming next update")


if __name__ == "__main__":
    app = App()
    app.mainloop()
