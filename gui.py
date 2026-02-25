import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import threading
import json
import os
import logging

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
        root.geometry("1200x850")

        self.cards = []
        self.horses = []
        self.images_cache = {}

        notebook = ttk.Notebook(root)
        notebook.pack(fill="both", expand=True)

        # ---------- TAB 1: Planner ----------
        self.plan_tab = ttk.Frame(notebook)
        notebook.add(self.plan_tab, text="Deck Planner")

        # ---------- TAB 2: All Cards ----------
        self.cards_tab = ttk.Frame(notebook)
        notebook.add(self.cards_tab, text="All Support Cards")

        self.build_planner_tab()
        self.build_cards_tab()

        self.load_data()

    # ======================================================
    # TAB 1 - PLANNER
    # ======================================================

    def build_planner_tab(self):

        top = ttk.Frame(self.plan_tab)
        top.pack(fill="x", pady=5)

        self.update_btn = ttk.Button(top, text="Update Database", command=self.update_db)
        self.update_btn.pack(side="left", padx=5)

        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(top, maximum=100, variable=self.progress_var)
        self.progress.pack(fill="x", expand=True, padx=5)

        self.status_label = ttk.Label(self.plan_tab, text="Ready")
        self.status_label.pack()

        # Scenario
        ttk.Label(self.plan_tab, text="Scenario").pack()
        self.scenario_var = tk.StringVar()
        self.scenario_box = ttk.Combobox(self.plan_tab, textvariable=self.scenario_var, state="readonly")
        self.scenario_box["values"] = SCENARIOS
        self.scenario_box.current(0)
        self.scenario_box.pack(pady=5)

        # Horse
        ttk.Label(self.plan_tab, text="Horse").pack()
        self.horse_var = tk.StringVar()
        self.horse_box = ttk.Combobox(self.plan_tab, textvariable=self.horse_var, state="readonly")
        self.horse_box.pack(pady=5)

        self.recommend_btn = ttk.Button(self.plan_tab, text="Recommend Best Deck", command=self.recommend)
        self.recommend_btn.pack(pady=10)

        self.result_box = tk.Text(self.plan_tab, height=12)
        self.result_box.pack(fill="x", padx=20)

    # ======================================================
    # TAB 2 - ALL SUPPORT CARDS
    # ======================================================

    def build_cards_tab(self):

        self.tree = ttk.Treeview(self.cards_tab, columns=("Type", "Rarity", "Blacklisted"), show="headings")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Rarity", text="Rarity")
        self.tree.heading("Blacklisted", text="Blacklisted")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<Double-1>", self.toggle_blacklist_from_list)

    # ======================================================
    # DATABASE
    # ======================================================

    def update_db(self):
        self.update_btn.config(state="disabled")
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        crawl(progress_callback=self.update_progress, status_callback=self.update_status)
        self.load_data()
        self.update_btn.config(state="normal")

    def update_progress(self, value):
        self.progress_var.set(value)

    def update_status(self, text):
        self.status_label.config(text=text)

    # ======================================================
    # LOAD DATA
    # ======================================================

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

        self.populate_card_list()

    def populate_card_list(self):

        for row in self.tree.get_children():
            self.tree.delete(row)

        for card in self.cards:
            self.tree.insert(
                "",
                "end",
                iid=str(card["id"]),
                values=(
                    card.get("type", "Unknown"),
                    card.get("rarity", "SR"),
                    "Yes" if card.get("blacklisted") else "No"
                )
            )

    def toggle_blacklist_from_list(self, event):

        item = self.tree.selection()[0]
        card_id = int(item)

        for card in self.cards:
            if card["id"] == card_id:
                card["blacklisted"] = not card.get("blacklisted", False)

        self.save_data()
        self.populate_card_list()

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump({"horses": self.horses, "cards": self.cards}, f, indent=2)

    # ======================================================
    # RECOMMEND
    # ======================================================

    def recommend(self):

        horse_name = self.horse_var.get()
        scenario = self.scenario_var.get()

        horse = next(h for h in self.horses if h["name"] == horse_name)

        deck = recommend_deck(
            horse,
            scenario,
            [c for c in self.cards if not c.get("blacklisted")]
        )

        self.result_box.delete("1.0", tk.END)

        for card in deck:
            self.result_box.insert(tk.END, f"{card['name']} ({card['type']})\n")


def start_app():
    root = tk.Tk()
    App(root)
    root.mainloop()
