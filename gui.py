import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import json
import os
import threading
from crawler import crawl

DATA_FILE = "data/data.json"


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Deck Builder")
        self.root.geometry("1200x800")

        self.data = {"horses": [], "cards": []}
        self.images_cache = {}

        self.build_layout()
        self.load_data()

    # ---------------- UI ----------------

    def build_layout(self):

        top = ttk.Frame(self.root)
        top.pack(fill="x")

        self.update_btn = ttk.Button(top, text="Update Database", command=self.update_data)
        self.update_btn.pack(side="left", padx=5)

        self.scenario = ttk.Combobox(top, values=["URA", "Aoharu", "Grand Live"])
        self.scenario.current(0)
        self.scenario.pack(side="left", padx=5)

        self.char_select = ttk.Combobox(top)
        self.char_select.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(top, length=300)
        self.progress.pack(side="left", padx=10)

        self.status_label = ttk.Label(top, text="Ready")
        self.status_label.pack(side="left")

        self.count_label = ttk.Label(self.root, text="")
        self.count_label.pack()

        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill="both", expand=True)

        self.frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    # ---------------- DATA ----------------

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)

        self.char_select["values"] = [h["name"] for h in self.data["horses"]]

        self.count_label.config(
            text=f"Horses: {len(self.data['horses'])} | Cards: {len(self.data['cards'])}"
        )

        self.draw_cards()

    # ---------------- DRAW ----------------

    def draw_cards(self):

        for widget in self.frame.winfo_children():
            widget.destroy()

        cols = 6
        for i, card in enumerate(self.data["cards"]):
            row = i // cols
            col = i % cols

            f = ttk.Frame(self.frame)
            f.grid(row=row, column=col, padx=5, pady=5)

            img = self.get_image(card["image"])
            lbl = tk.Label(f, image=img)
            lbl.image = img
            lbl.pack()

            lbl.bind("<Button-1>", lambda e, c=card: self.add_star(c))
            lbl.bind("<Button-3>", lambda e, c=card: self.toggle_blacklist(c))

            star_lbl = ttk.Label(f, text="★"*card.get("stars", 0))
            star_lbl.pack()

            name_lbl = ttk.Label(f, text=card["name"], wraplength=120)
            name_lbl.pack()

            if card.get("blacklisted"):
                lbl.config(bg="gray")

    # ---------------- IMAGE ----------------

    def get_image(self, path):
        if not os.path.exists(path):
            img = Image.new("RGB", (128, 128), color="gray")
        else:
            img = Image.open(path).resize((128, 128))

        return ImageTk.PhotoImage(img)

    # ---------------- INTERACTION ----------------

    def add_star(self, card):
        card["stars"] = (card.get("stars", 0) + 1) % 5
        self.save()
        self.draw_cards()

    def toggle_blacklist(self, card):
        card["blacklisted"] = not card.get("blacklisted", False)
        self.save()
        self.draw_cards()

    # ---------------- SAVE ----------------

    def save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    # ---------------- UPDATE ----------------

    def update_data(self):

        def progress(section, current, total):
            self.progress["maximum"] = total
            self.progress["value"] = current
            self.status_label.config(text=f"{section}: {current}/{total}")

        def task():
            crawl(progress)
            self.load_data()
            self.status_label.config(text="Done")

        threading.Thread(target=task).start()


def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
