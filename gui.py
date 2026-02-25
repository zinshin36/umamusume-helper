import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import json
import os

from crawler import crawl
from planner import recommend_deck

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
        root.title("Uma Planner PRO")
        root.geometry("1200x900")

        self.cards = []
        self.horses = []
        self.images_cache = {}

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        self.plan_tab = ttk.Frame(notebook)
        self.cards_tab = ttk.Frame(notebook)

        notebook.add(self.plan_tab, text="Deck Planner")
        notebook.add(self.cards_tab, text="All Support Cards")

        self.build_planner_tab()
        self.build_cards_tab()

        self.load_data()

    # ------------------------
    # Planner Tab
    # ------------------------

    def build_planner_tab(self):

        top = ttk.Frame(self.plan_tab)
        top.pack(fill="x")

        self.update_btn = ttk.Button(top, text="Update Database", command=self.update_db)
        self.update_btn.pack(side="left")

        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(top, maximum=100, variable=self.progress_var)
        self.progress.pack(fill="x", expand=True, padx=10)

        self.status_label = ttk.Label(self.plan_tab, text="Ready")
        self.status_label.pack()

        ttk.Label(self.plan_tab, text="Scenario").pack()
        self.scenario_var = tk.StringVar()
        self.scenario_box = ttk.Combobox(self.plan_tab, textvariable=self.scenario_var, state="readonly")
        self.scenario_box["values"] = SCENARIOS
        self.scenario_box.current(0)
        self.scenario_box.pack()

        ttk.Label(self.plan_tab, text="Horse").pack()
        self.horse_var = tk.StringVar()
        self.horse_box = ttk.Combobox(self.plan_tab, textvariable=self.horse_var, state="readonly")
        self.horse_box.pack()

        self.recommend_btn = ttk.Button(self.plan_tab, text="Recommend Best Deck", command=self.recommend)
        self.recommend_btn.pack(pady=10)

        self.deck_frame = ttk.Frame(self.plan_tab)
        self.deck_frame.pack(pady=10)

    # ------------------------
    # Cards Tab
    # ------------------------

    def build_cards_tab(self):

        self.cards_canvas = tk.Canvas(self.cards_tab)
        self.cards_scroll = ttk.Scrollbar(self.cards_tab, orient="vertical", command=self.cards_canvas.yview)
        self.cards_inner = ttk.Frame(self.cards_canvas)

        self.cards_inner.bind(
            "<Configure>",
            lambda e: self.cards_canvas.configure(scrollregion=self.cards_canvas.bbox("all"))
        )

        self.cards_canvas.create_window((0, 0), window=self.cards_inner, anchor="nw")
        self.cards_canvas.configure(yscrollcommand=self.cards_scroll.set)

        self.cards_canvas.pack(side="left", fill="both", expand=True)
        self.cards_scroll.pack(side="right", fill="y")

    # ------------------------
    # Update DB
    # ------------------------

    def update_db(self):
        self.update_btn.config(state="disabled")
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        crawl(
            progress_callback=lambda v: self.root.after(0, self.progress_var.set, v),
            status_callback=lambda s: self.root.after(0, self.status_label.config, {"text": s})
        )
        self.root.after(0, self.load_data)
        self.root.after(0, lambda: self.update_btn.config(state="normal"))

    # ------------------------
    # Load Data
    # ------------------------

    def load_data(self):

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.horses = data["horses"]
        self.cards = data["cards"]

        self.horse_box["values"] = [h["name"] for h in self.horses]
        if self.horses:
            self.horse_box.current(0)

        self.populate_cards_tab()

    def populate_cards_tab(self):

        for widget in self.cards_inner.winfo_children():
            widget.destroy()

        for card in self.cards:

            frame = ttk.Frame(self.cards_inner)
            frame.pack(fill="x", pady=5)

            img_path = card.get("image")
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((60, 80))
                photo = ImageTk.PhotoImage(img)
                self.images_cache[card["id"]] = photo
                label_img = ttk.Label(frame, image=photo)
                label_img.pack(side="left")

            name_label = ttk.Label(frame, text=card["name"])
            name_label.pack(side="left", padx=10)

            btn = ttk.Button(
                frame,
                text="Blacklist" if not card.get("blacklisted") else "Unblacklist",
                command=lambda c=card: self.toggle_blacklist(c)
            )
            btn.pack(side="right")

    def toggle_blacklist(self, card):
        card["blacklisted"] = not card.get("blacklisted", False)
        self.save_data()
        self.populate_cards_tab()

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"horses": self.horses, "cards": self.cards}, f, indent=2)

    # ------------------------
    # Recommend
    # ------------------------

    def recommend(self):

        for widget in self.deck_frame.winfo_children():
            widget.destroy()

        horse_name = self.horse_var.get()
        scenario = self.scenario_var.get()

        horse = next(h for h in self.horses if h["name"] == horse_name)

        deck = recommend_deck(horse, scenario, self.cards)

        for card in deck:
            if os.path.exists(card["image"]):
                img = Image.open(card["image"]).resize((100, 140))
                photo = ImageTk.PhotoImage(img)
                self.images_cache[f"deck_{card['id']}"] = photo
                label = ttk.Label(self.deck_frame, image=photo)
                label.pack(side="left", padx=5)


def start_app():
    root = tk.Tk()
    App(root)
    root.mainloop()
