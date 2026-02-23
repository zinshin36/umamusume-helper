import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
from pathlib import Path

DATA_FILE = "data/data.json"


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Uma DB Viewer")
        self.geometry("1000x700")

        self.horses = []
        self.cards = []

        self.create_widgets()
        self.load_data()

    def create_widgets(self):

        self.top_frame = tk.Frame(self)
        self.top_frame.pack(fill="x")

        self.horse_label = tk.Label(self.top_frame, text="Horses: 0")
        self.horse_label.pack(side="left", padx=10)

        self.card_label = tk.Label(self.top_frame, text="Support Cards: 0")
        self.card_label.pack(side="left", padx=10)

        self.refresh_button = tk.Button(
            self.top_frame,
            text="Reload Data",
            command=self.load_data
        )
        self.refresh_button.pack(side="right", padx=10)

        self.canvas = tk.Canvas(self)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
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

        self.display_images(self.horses)

    def display_images(self, items):

        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        self.images = []

        cols = 4
        row = 0
        col = 0

        for item in items:
            if not item["image"]:
                continue

            try:
                img = Image.open(item["image"])
                img = img.resize((150, 200))
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)

                frame = tk.Frame(self.scroll_frame)
                frame.grid(row=row, column=col, padx=10, pady=10)

                label = tk.Label(frame, image=photo)
                label.pack()

                name = tk.Label(frame, text=item["name"], wraplength=150)
                name.pack()

                col += 1
                if col >= cols:
                    col = 0
                    row += 1

            except:
                continue


if __name__ == "__main__":
    app = App()
    app.mainloop()
