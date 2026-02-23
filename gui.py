import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os

DATA_FILE = "data/data.json"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Uma Database Viewer")
        self.geometry("1100x750")

        self.horses = []
        self.cards = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):

        top = tk.Frame(self)
        top.pack(fill="x")

        self.horse_label = tk.Label(top, text="Horses: 0")
        self.horse_label.pack(side="left", padx=10)

        self.card_label = tk.Label(top, text="Support Cards: 0")
        self.card_label.pack(side="left", padx=10)

        self.reload_btn = tk.Button(
            top,
            text="Reload Data",
            command=self.load_data
        )
        self.reload_btn.pack(side="right", padx=10)

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

    def load_data(self):

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.horses = data.get("horses", [])
        self.cards = data.get("cards", [])

        self.horse_label.config(text=f"Horses: {len(self.horses)}")
        self.card_label.config(text=f"Support Cards: {len(self.cards)}")

        self.display_items(self.horses)

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
                img = img.resize((140, 190))
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)

                frame = tk.Frame(self.scroll_frame)
                frame.grid(row=row, column=col, padx=10, pady=10)

                img_label = tk.Label(frame, image=photo)
                img_label.pack()

                name_label = tk.Label(frame, text=item["name"], wraplength=140)
                name_label.pack()

                col += 1
                if col >= cols:
                    col = 0
                    row += 1

            except:
                continue
