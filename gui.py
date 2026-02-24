import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import json
import os
import logging
import random

from crawler import crawl

DATA_FILE = "data/data.json"
IMG_SUPPORT_DIR = "data/images/support"

SCENARIOS = [
    "URA",
    "Aoharu",
    "Grand Live",
    "Make a New Track",
    "Project L'Arc"
]


class App:

    def __init__(self, root):
        self.root = root
        root.title("Uma Planner")
        root.geometry("1000x800")

        self.cards = []
        self.horses = []
        self.card_widgets = {}
        self.images_cache = {}

        # --- Top Controls ---
        top = ttk.Frame(root)
        top.pack(fill="x", pady=5)

        self.update_btn = ttk.Button(top, text="Update Database", command=self.update_db)
        self.update_btn.pack(side="left", padx=5)

        self.recommend_btn = ttk.Button(top, text="Recommend Deck", command=self.recommend_deck)
        self.recommend_btn.pack(side="left", padx=5)

        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(top, maximum=100, variable=self.progress_var)
        self.progress.pack(fill="x", expand=True, padx=5)

        self.status = ttk.Label(root, text="Ready")
        self.status.pack()

        # --- Scenario Dropdown ---
        self.scenario_var = tk.StringVar()
        self.scenario_box = ttk.Combobox(root, textvariable=self.scenario_var, state="readonly")
        self.scenario_box["values"] = SCENARIOS
        self.scenario_box.current(0)
        self.scenario_box.pack(pady=5)

        # --- Horse Dropdown ---
        self.horse_var = tk.StringVar()
        self.horse_box = ttk.Combobox(root, textvariable=self.horse_var, state="readonly")
        self.horse_box.pack(pady=5)

        # --- Scrollable Card Frame ---
        container = ttk.Frame(root)
        container.pack(fill="both", expand=True)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.card_frame = ttk.Frame(canvas)

        self.card_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.card_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Recommended Deck Output ---
        self.deck_output = ttk.Label(root, text="Recommended Deck: None")
        self.deck_output.pack(pady=10)

        self.count_label = ttk.Label(root, text="Horses: 0 Cards: 0")
        self.count_label.pack()

        self.load_data()

    # -----------------------
    # Database Update
    # -----------------------

    def update_db(self):
        self.update_btn.config(state="disabled")
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        crawl(progress=self.progress_var.set, status=self.status.config)
        self.load_data()
        self.update_btn.config(state="normal")

    # -----------------------
    # Load Data
    # -----------------------

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.horses = data["horses"]
        self.cards = data["cards"]

        self.count_label.config(
            text=f"Horses: {len(self.horses)} Cards: {len(self.cards)}"
        )

        horse_names = [h["name"] for h in self.horses]
        self.horse_box["values"] = horse_names
        if horse_names:
            self.horse_box.current(0)

        self.render_cards()

    # -----------------------
    # Render Support Cards
    # -----------------------

    def render_cards(self):

        for widget in self.card_frame.winfo_children():
            widget.destroy()

        self.card_widgets.clear()

        for index, card in enumerate(self.cards):

            frame = tk.Frame(self.card_frame, bd=2, relief="solid")
            frame.grid(row=index // 5, column=index % 5, padx=5, pady=5)

            img_path = card["image"]

            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                self.images_cache[card["id"]] = photo

                label = tk.Label(frame, image=photo)
                label.pack()
            else:
                label = tk.Label(frame, text="No Image")
                label.pack()

            name_label = tk.Label(frame, text=card["name"], wraplength=100)
            name_label.pack()

            frame.bind("<Button-1>", lambda e, c=card: self.toggle_blacklist(c))
            label.bind("<Button-1>", lambda e, c=card: self.toggle_blacklist(c))

            self.card_widgets[card["id"]] = frame

            if card.get("blacklisted"):
                frame.config(highlightbackground="red", highlightthickness=3)

    # -----------------------
    # Blacklist Toggle
    # -----------------------

    def toggle_blacklist(self, card):
        card["blacklisted"] = not card.get("blacklisted", False)

        frame = self.card_widgets[card["id"]]

        if card["blacklisted"]:
            frame.config(highlightbackground="red", highlightthickness=3)
        else:
            frame.config(highlightthickness=0)

        self.save_data()

    # -----------------------
    # Save Data
    # -----------------------

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"horses": self.horses, "cards": self.cards}, f, indent=2)

    # -----------------------
    # Recommend Deck
    # -----------------------

    def recommend_deck(self):

        selected_horse = self.horse_var.get()
        if not selected_horse:
            return

        available_cards = [
            c for c in self.cards if not c.get("blacklisted")
        ]

        if len(available_cards) < 6:
            self.deck_output.config(text="Not enough cards available.")
            return

        deck = random.sample(available_cards, 6)

        deck_names = [c["name"] for c in deck]

        self.deck_output.config(
            text="Recommended Deck:\n" + "\n".join(deck_names)
        )


def start_app():
    root = tk.Tk()
    App(root)
    root.mainloop()
