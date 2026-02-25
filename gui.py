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

SCENARIOS = [
    "URA",
    "Aoharu",
    "Grand Live",
    "Make a New Track",
    "Project L'Arc"
]


class UmaPlannerApp:

    def __init__(self, root):

        self.root = root
        self.root.title("Uma Planner PRO")
        self.root.geometry("1300x900")

        logging.basicConfig(
            filename="app.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        logging.info("Application started")

        self.horses = []
        self.cards = []
        self.image_cache = {}

        self.build_ui()
        self.load_data()

    # =====================================================
    # UI BUILD
    # =====================================================

    def build_ui(self):

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True)

        self.planner_tab = ttk.Frame(notebook)
        self.cards_tab = ttk.Frame(notebook)

        notebook.add(self.planner_tab, text="Deck Planner")
        notebook.add(self.cards_tab, text="All Support Cards")

        self.build_planner_tab()
        self.build_cards_tab()

    # =====================================================
    # PLANNER TAB
    # =====================================================

    def build_planner_tab(self):

        top_frame = ttk.Frame(self.planner_tab)
        top_frame.pack(fill="x", pady=5)

        self.update_btn = ttk.Button(
            top_frame,
            text="Update Database",
            command=self.start_update
        )
        self.update_btn.pack(side="left", padx=5)

        self.progress_var = tk.IntVar(value=0)

        self.progress_bar = ttk.Progressbar(
            top_frame,
            maximum=100,
            variable=self.progress_var
        )
        self.progress_bar.pack(side="left", fill="x", expand=True, padx=10)

        self.percent_label = ttk.Label(top_frame, text="0%")
        self.percent_label.pack(side="right", padx=5)

        self.status_label = ttk.Label(self.planner_tab, text="Ready")
        self.status_label.pack()

        ttk.Label(self.planner_tab, text="Scenario").pack(pady=5)

        self.scenario_var = tk.StringVar()
        self.scenario_box = ttk.Combobox(
            self.planner_tab,
            textvariable=self.scenario_var,
            state="readonly"
        )
        self.scenario_box["values"] = SCENARIOS
        self.scenario_box.current(0)
        self.scenario_box.pack()

        ttk.Label(self.planner_tab, text="Horse").pack(pady=5)

        self.horse_var = tk.StringVar()
        self.horse_box = ttk.Combobox(
            self.planner_tab,
            textvariable=self.horse_var,
            state="readonly"
        )
        self.horse_box.pack()

        self.recommend_btn = ttk.Button(
            self.planner_tab,
            text="Recommend Best Deck",
            command=self.recommend_deck_ui
        )
        self.recommend_btn.pack(pady=10)

        self.deck_frame = ttk.Frame(self.planner_tab)
        self.deck_frame.pack(pady=10)

    # =====================================================
    # CARDS TAB
    # =====================================================

    def build_cards_tab(self):

        self.canvas = tk.Canvas(self.cards_tab)
        self.scrollbar = ttk.Scrollbar(
            self.cards_tab,
            orient="vertical",
            command=self.canvas.yview
        )

        self.cards_inner = ttk.Frame(self.canvas)

        self.cards_inner.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window(
            (0, 0),
            window=self.cards_inner,
            anchor="nw"
        )

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    # =====================================================
    # UPDATE DATABASE
    # =====================================================

    def start_update(self):

        self.update_btn.config(state="disabled")
        self.progress_var.set(0)
        self.percent_label.config(text="0%")
        self.status_label.config(text="Starting...")

        thread = threading.Thread(
            target=self.run_crawl_thread,
            daemon=True
        )
        thread.start()

    def run_crawl_thread(self):

        def progress_update(value):
            self.root.after(
                0,
                lambda: self.update_progress(value)
            )

        def status_update(text):
            self.root.after(
                0,
                lambda: self.status_label.config(text=text)
            )

        crawl(
            progress_callback=progress_update,
            status_callback=status_update
        )

        self.root.after(0, self.load_data)
        self.root.after(
            0,
            lambda: self.update_btn.config(state="normal")
        )

    def update_progress(self, value):
        self.progress_var.set(value)
        self.percent_label.config(text=f"{value}%")

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(self):

        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.horses = data.get("horses", [])
        self.cards = data.get("cards", [])

        self.horse_box["values"] = [h["name"] for h in self.horses]

        if self.horses:
            self.horse_box.current(0)

        self.populate_cards_tab()

    # =====================================================
    # SUPPORT CARD LIST
    # =====================================================

    def populate_cards_tab(self):

        for widget in self.cards_inner.winfo_children():
            widget.destroy()

        for card in self.cards:

            frame = ttk.Frame(self.cards_inner)
            frame.pack(fill="x", pady=3)

            img_path = card.get("image")

            if img_path and os.path.exists(img_path):

                try:
                    img = Image.open(img_path).resize((60, 80))
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[card["id"]] = photo

                    img_label = ttk.Label(frame, image=photo)
                    img_label.pack(side="left", padx=5)

                except Exception:
                    pass

            name_label = ttk.Label(frame, text=card["name"])
            name_label.pack(side="left", padx=10)

            btn_text = (
                "Unblacklist"
                if card.get("blacklisted")
                else "Blacklist"
            )

            btn = ttk.Button(
                frame,
                text=btn_text,
                command=lambda c=card: self.toggle_blacklist(c)
            )
            btn.pack(side="right")

    def toggle_blacklist(self, card):

        card["blacklisted"] = not card.get("blacklisted", False)

        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {"horses": self.horses, "cards": self.cards},
                f,
                indent=2
            )

        self.populate_cards_tab()

    # =====================================================
    # RECOMMEND DECK
    # =====================================================

    def recommend_deck_ui(self):

        for widget in self.deck_frame.winfo_children():
            widget.destroy()

        if not self.horses:
            return

        horse_name = self.horse_var.get()
        scenario = self.scenario_var.get()

        horse = next(
            (h for h in self.horses if h["name"] == horse_name),
            None
        )

        if not horse:
            return

        deck = recommend_deck(
            horse,
            scenario,
            self.cards
        )

        for card in deck:

            img_path = card.get("image")

            if img_path and os.path.exists(img_path):

                try:
                    img = Image.open(img_path).resize((120, 160))
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[f"deck_{card['id']}"] = photo

                    label = ttk.Label(
                        self.deck_frame,
                        image=photo
                    )
                    label.pack(side="left", padx=5)

                except Exception:
                    pass


# =====================================================
# START
# =====================================================

def start_app():
    root = tk.Tk()
    app = UmaPlannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    start_app()
