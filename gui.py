import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from crawler import crawl
from data_manager import ensure_data_exists, load_data, toggle_blacklist, set_stars, load_state
from recommendation_engine import recommend_deck, recommend_legacy


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Smart Builder")

        ensure_data_exists(crawl)
        self.data = load_data()

        self.build_ui()

    def build_ui(self):
        top = tk.Frame(self.root)
        top.pack()

        tk.Button(top, text="Update", command=self.update_data).pack()

        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        self.display_horses()

    def display_horses(self):
        for w in self.grid_frame.winfo_children():
            w.destroy()

        for i, horse in enumerate(self.data["horses"]):
            img = Image.open(horse["image"]).resize((80, 80))
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(self.grid_frame, image=photo,
                            command=lambda h=horse: self.open_builder(h))
            btn.image = photo
            btn.grid(row=i // 6, column=i % 6)

    def open_builder(self, horse):
        win = tk.Toplevel(self.root)
        win.title(horse["name"])

        deck = recommend_deck(horse, self.data["cards"])
        legacy = recommend_legacy(horse, self.data["horses"])

        tk.Label(win, text="Recommended Deck").pack()

        state = load_state()

        for card in deck:
            frame = tk.Frame(win)
            frame.pack()

            img = Image.open(card["image"]).resize((70, 70))
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(frame, image=photo)
            btn.image = photo
            btn.pack(side=tk.LEFT)

            if card["id"] in state["blacklist"]:
                btn.config(state="disabled")

            tk.Button(frame, text="Blacklist",
                      command=lambda cid=card["id"]: toggle_blacklist(cid)).pack(side=tk.LEFT)

            tk.Button(frame, text="⭐ +1",
                      command=lambda cid=card["id"]: set_stars(cid, 5)).pack(side=tk.LEFT)

        tk.Label(win, text="Recommended Legacy").pack()

        for parent in legacy:
            tk.Label(win, text=parent["name"]).pack()

    def update_data(self):
        crawl()
        self.data = load_data()
        self.display_horses()
        messagebox.showinfo("Done", "Updated successfully")


def run():
    root = tk.Tk()
    app = App(root)
    root.mainloop()
