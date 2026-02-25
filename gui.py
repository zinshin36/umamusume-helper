import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import os

from api import UmaAPI
from optimizer import DeckOptimizer
from data_manager import DataManager


class UmaPlannerGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Planner PRO")
        self.root.geometry("1200x800")

        self.data_manager = DataManager()
        self.horses, self.supports = self.data_manager.load()

        self.images_cache = {}

        self.build_ui()
        self.refresh_dropdowns()
        self.load_support_tab()

    # ================= UI =================

    def build_ui(self):

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True)

        self.deck_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.deck_frame, text="Deck Planner")

        self.support_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.support_tab, text="All Support Cards")

        self.build_deck_tab()
        self.build_support_tab()

    # ================= DECK TAB =================

    def build_deck_tab(self):

        top_frame = ttk.Frame(self.deck_frame)
        top_frame.pack(fill="x", pady=5)

        self.update_btn = ttk.Button(top_frame, text="Update Database", command=self.start_update)
        self.update_btn.pack(side="left", padx=5)

        self.progress = ttk.Progressbar(top_frame, length=400, maximum=100)
        self.progress.pack(side="left", padx=10)

        self.status_label = ttk.Label(top_frame, text="Ready")
        self.status_label.pack(side="left")

        options_frame = ttk.Frame(self.deck_frame)
        options_frame.pack(pady=10)

        ttk.Label(options_frame, text="Scenario").grid(row=0, column=0)
        self.scenario_var = tk.StringVar(value="Aoharu")
        self.scenario_dropdown = ttk.Combobox(
            options_frame,
            textvariable=self.scenario_var,
            values=["Aoharu", "URA", "Grand Live"],
            state="readonly"
        )
        self.scenario_dropdown.grid(row=0, column=1)

        ttk.Label(options_frame, text="Horse").grid(row=1, column=0)
        self.horse_var = tk.StringVar()
        self.horse_dropdown = ttk.Combobox(
            options_frame,
            textvariable=self.horse_var,
            state="readonly"
        )
        self.horse_dropdown.grid(row=1, column=1)

        self.simulation_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options_frame,
            text="Simulation Mode (Competitive)",
            variable=self.simulation_var
        ).grid(row=2, columnspan=2, pady=5)

        ttk.Button(
            options_frame,
            text="Recommend Best Deck",
            command=self.recommend_deck
        ).grid(row=3, columnspan=2, pady=10)

        self.deck_display = ttk.Frame(self.deck_frame)
        self.deck_display.pack(pady=20)

    # ================= SUPPORT TAB =================

    def build_support_tab(self):

        canvas = tk.Canvas(self.support_tab)
        scrollbar = ttk.Scrollbar(self.support_tab, orient="vertical", command=canvas.yview)
        self.support_container = ttk.Frame(canvas)

        self.support_container.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.support_container, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ================= UPDATE =================

    def start_update(self):
        self.update_btn.config(state="disabled")
        self.progress["value"] = 0
        self.status_label.config(text="Connecting to API...")

        thread = threading.Thread(target=self.update_database)
        thread.start()

    def update_database(self):

        api = UmaAPI(progress_callback=self.update_progress)

        horses = api.fetch_all_horses()
        supports = api.fetch_all_supports()

        self.data_manager.save(horses, supports)

        self.horses = horses
        self.supports = supports

        self.root.after(0, self.update_complete)

    def update_progress(self, message, page):
        def update():
            self.status_label.config(text=message)
            self.progress["value"] = min(100, page)
        self.root.after(0, update)

    def update_complete(self):
        self.progress["value"] = 100
        self.status_label.config(text="Crawl complete")
        self.update_btn.config(state="normal")
        self.refresh_dropdowns()
        self.load_support_tab()

    # ================= DROPDOWNS =================

    def refresh_dropdowns(self):

        horse_names = [h["name"] for h in self.horses]
        self.horse_dropdown["values"] = horse_names

        if horse_names:
            self.horse_dropdown.current(0)

    # ================= RECOMMEND =================

    def recommend_deck(self):

        if not self.horses or not self.supports:
            messagebox.showerror("Error", "Database not loaded")
            return

        selected_horse_name = self.horse_var.get()
        selected_horse = next(h for h in self.horses if h["name"] == selected_horse_name)

        optimizer = DeckOptimizer(
            self.supports,
            selected_horse,
            self.scenario_var.get(),
            simulation_mode=self.simulation_var.get()
        )

        deck = optimizer.build_best_deck()

        for widget in self.deck_display.winfo_children():
            widget.destroy()

        for i, support in enumerate(deck):
            img = self.load_image(support["image"])
            label = tk.Label(self.deck_display, image=img)
            label.image = img
            label.grid(row=0, column=i, padx=10)

    # ================= SUPPORT TAB =================

    def load_support_tab(self):

        for widget in self.support_container.winfo_children():
            widget.destroy()

        for idx, support in enumerate(self.supports):

            frame = ttk.Frame(self.support_container)
            frame.grid(row=idx // 3, column=idx % 3, padx=10, pady=10)

            img = self.load_image(support["image"])
            label = tk.Label(frame, image=img)
            label.image = img
            label.pack()

            ttk.Label(frame, text=f"{support['name']} ({support['rarity']})").pack()

            btn_text = "Unblacklist" if support.get("blacklisted") else "Blacklist"
            btn = ttk.Button(frame, text=btn_text,
                             command=lambda s=support: self.toggle_blacklist(s))
            btn.pack(pady=5)

    def toggle_blacklist(self, support):
        support["blacklisted"] = not support.get("blacklisted", False)
        self.data_manager.save(self.horses, self.supports)
        self.load_support_tab()

    # ================= IMAGE =================

    def load_image(self, path):

        if not os.path.exists(path):
            return ImageTk.PhotoImage(Image.new("RGB", (150, 150), "gray"))

        if path in self.images_cache:
            return self.images_cache[path]

        img = Image.open(path)
        img = img.resize((150, 150))
        tk_img = ImageTk.PhotoImage(img)

        self.images_cache[path] = tk_img
        return tk_img


# ✅ THIS FIXES YOUR IMPORT ERROR
def start_app():
    root = tk.Tk()
    app = UmaPlannerGUI(root)
    root.mainloop()
