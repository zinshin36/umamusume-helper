import tkinter as tk
from tkinter import ttk
import threading
import json
import os
import logging

from crawler import crawl

DATA_FILE = "data/data.json"

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
        root.geometry("600x500")

        self.top = ttk.Frame(root)
        self.top.pack(fill="x", pady=5)

        self.update_btn = ttk.Button(self.top, text="Update Database", command=self.update_db)
        self.update_btn.pack(side="left", padx=5)

        self.progress_var = tk.IntVar()
        self.progress = ttk.Progressbar(self.top, maximum=100, variable=self.progress_var)
        self.progress.pack(fill="x", expand=True, padx=5)

        self.status = ttk.Label(root, text="Ready")
        self.status.pack(pady=5)

        self.scenario_var = tk.StringVar()
        self.scenario_box = ttk.Combobox(root, textvariable=self.scenario_var, state="readonly")
        self.scenario_box["values"] = SCENARIOS
        self.scenario_box.current(0)
        self.scenario_box.pack(pady=5)

        self.horse_var = tk.StringVar()
        self.horse_box = ttk.Combobox(root, textvariable=self.horse_var, state="readonly")
        self.horse_box.pack(pady=5)

        self.count_label = ttk.Label(root, text="Horses: 0 Cards: 0")
        self.count_label.pack(pady=5)

        self.load_data()

    def update_progress(self, percent):
        self.progress_var.set(percent)

    def update_status(self, text):
        self.status.config(text=text)

    def update_db(self):
        self.update_btn.config(state="disabled")
        self.status.config(text="Starting crawl...")
        threading.Thread(target=self.run_crawl, daemon=True).start()

    def run_crawl(self):
        crawl(progress=self.update_progress, status=self.update_status)
        self.load_data()
        self.update_btn.config(state="normal")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        horses = data["horses"]
        cards = data["cards"]

        self.count_label.config(text=f"Horses: {len(horses)} Cards: {len(cards)}")

        horse_names = [h["name"] for h in horses]
        self.horse_box["values"] = horse_names

        if horse_names:
            self.horse_box.current(0)


def start_app():
    root = tk.Tk()
    App(root)
    root.mainloop()
