import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import json
import os

from crawler import crawl
from recommendation_engine import recommend
from data_manager import toggle_blacklist, set_stars, load_state


DATA_FILE = "data/data.json"


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Builder")

        self.load_data()

        self.build_ui()

    def load_data(self):
        with open(DATA_FILE, "r") as f:
            self.data = json.load(f)

    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack()

        update_btn = tk.Button(top, text="Update", command=self.update_data)
        update_btn.pack(side=tk.LEFT)

        self.horse_frame = tk.Frame(self.root)
        self.horse_frame.pack()

        self.display_horses()

    def display_horses(self):
        for widget in self.horse_frame.winfo_children():
            widget.destroy()

        for i, horse in enumerate(self.data["horses"]):
            img = Image.open(horse["image"]).resize((80, 80))
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(self.horse_frame, image=photo,
                            command=lambda h=horse: self.select_horse(h))
            btn.image = photo
            btn.grid(row=i // 6, column=i % 6)

    def select_horse(self, horse):
        rec = recommend(horse, self.data["cards"])
        self.show_recommendations(rec)

    def show_recommendations(self, cards):
        win = tk.Toplevel(self.root)
        win.title("Recommended")

        state = load_state()

        for i, card in enumerate(cards):
            frame = tk.Frame(win)
            frame.grid(row=i, column=0)

            img = Image.open(card["image"]).resize((80, 80))
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(frame, image=photo)
            btn.image = photo
            btn.pack(side=tk.LEFT)

            if card["id"] in state["blacklist"]:
                btn.config(state="disabled")

            blacklist_btn = tk.Button(frame, text="Blacklist",
                                       command=lambda cid=card["id"]: toggle_blacklist(cid))
            blacklist_btn.pack(side=tk.LEFT)

            star_btn = tk.Button(frame, text="Add Star",
                                 command=lambda cid=card["id"]: set_stars(cid, 5))
            star_btn.pack(side=tk.LEFT)

    def update_data(self):
        crawl()
        self.load_data()
        self.display_horses()
        messagebox.showinfo("Done", "Updated successfully")


def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
