import tkinter as tk
from tkinter import ttk, messagebox
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

        self.percent_label = ttk.Label(top, text="0%")
        self.percent_label.pack(side="left")

        self.status_label = ttk.Label(top, text="Ready")
        self.status_label.pack(side="left", padx=10)

        self.count_label = ttk.Label(self.root, text="Horses: 0 | Cards: 0")
        self.count_label.pack()

    # ---------------- DATA ----------------

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.data = json.load(f)

        self.char_select["values"] = [h["name"] for h in self.data["horses"]]

        self.count_label.config(
            text=f"Horses: {len(self.data['horses'])} | Cards: {len(self.data['cards'])}"
        )

    # ---------------- UPDATE ----------------

    def update_data(self):

        self.update_btn.config(state="disabled")
        self.status_label.config(text="Starting...")
        self.percent_label.config(text="0%")
        self.progress["value"] = 0

        def progress(section, current, total):
            percent = int((current / total) * 100)
            self.progress["maximum"] = total
            self.progress["value"] = current
            self.percent_label.config(text=f"{percent}%")
            self.status_label.config(text=f"{section}: {current}/{total}")

            self.root.update_idletasks()

        def status(text):
            self.status_label.config(text=text)
            self.root.update_idletasks()

        def task():
            try:
                crawl(progress_callback=progress, status_callback=status)
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
            finally:
                self.update_btn.config(state="normal")
                self.status_label.config(text="Ready")

        threading.Thread(target=task, daemon=True).start()


def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
