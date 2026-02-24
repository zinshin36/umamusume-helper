import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from crawler import crawl
from data_manager import ensure_data_exists, load_data, load_state, toggle_blacklist, set_stars
from recommendation_engine import recommend_deck


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Smart Builder")
        self.root.geometry("1200x800")

        ensure_data_exists(crawl)
        self.data = load_data()

        self.build_layout()

    def build_layout(self):

        top = tk.Frame(self.root)
        top.pack(fill="x")

        tk.Button(top, text="Update", command=self.update).pack(side="left")

        self.scenario_var = tk.StringVar(value="URA")
        ttk.Combobox(top, textvariable=self.scenario_var,
                     values=["URA", "Aoharu", "Grand Live"]).pack(side="left")

        self.canvas = tk.Canvas(self.root)
        self.scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas)

        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.display_horses()

    def display_horses(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        for i, horse in enumerate(self.data["horses"]):
            img = Image.open(horse["image"]).resize((100, 100))
            photo = ImageTk.PhotoImage(img)

            btn = tk.Button(self.scroll_frame, image=photo,
                            command=lambda h=horse: self.open_builder(h))
            btn.image = photo
            btn.grid(row=i // 8, column=i % 8, padx=5, pady=5)

    def open_builder(self, horse):
        win = tk.Toplevel(self.root)
        win.geometry("1000x700")
        win.title(horse["name"])

        scenario = self.scenario_var.get()
        deck = recommend_deck(horse, self.data["cards"], scenario)
        state = load_state()

        for i, card in enumerate(deck):
            frame = tk.Frame(win, relief="ridge", bd=2)
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=10)

            img = Image.open(card["image"]).resize((120, 120))
            photo = ImageTk.PhotoImage(img)

            label = tk.Label(frame, image=photo)
            label.image = photo
            label.pack()

            stars = state["stars"].get(str(card["id"]), 0)

            star_frame = tk.Frame(frame)
            star_frame.pack()

            for s in range(5):
                def set_star(level=s, cid=card["id"]):
                    set_stars(cid, level)
                    win.destroy()
                    self.open_builder(horse)

                text = "★" if s < stars else "☆"
                tk.Button(star_frame, text=text,
                          command=set_star).pack(side="left")

            tk.Button(frame, text="Blacklist",
                      command=lambda cid=card["id"]: toggle_blacklist(cid)).pack()

    def update(self):
        crawl()
        self.data = load_data()
        self.display_horses()


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()
