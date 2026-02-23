import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import threading

from data_manager import load_data, save_data
from crawler import crawl_horses, crawl_support_cards
from recommender import recommend_cards


class UmaGui:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Uma Musume Helper")
        self.root.geometry("900x600")

        self.data = load_data()
        self.selected_horse = None
        self.image_cache = None

        self.build_ui()

    def build_ui(self):
        left_frame = tk.Frame(self.root)
        left_frame.pack(side="left", fill="y", padx=10, pady=10)

        self.horse_list = tk.Listbox(left_frame, width=30)
        self.horse_list.pack(fill="y")

        for horse in self.data["horses"]:
            self.horse_list.insert("end", horse["name"])

        self.horse_list.bind("<<ListboxSelect>>", self.on_horse_select)

        right_frame = tk.Frame(self.root)
        right_frame.pack(side="right", fill="both", expand=True)

        self.image_label = tk.Label(right_frame)
        self.image_label.pack(pady=10)

        self.progress = ttk.Progressbar(right_frame, mode="indeterminate")
        self.progress.pack(fill="x", pady=5)

        button_frame = tk.Frame(right_frame)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Check Updates", command=self.check_updates).pack(side="left", padx=5)
        tk.Button(button_frame, text="Recommended Cards", command=self.show_recommendations).pack(side="left", padx=5)
        tk.Button(button_frame, text="Blacklist Selected Card", command=self.blacklist_card).pack(side="left", padx=5)

        self.recommend_box = tk.Listbox(right_frame)
        self.recommend_box.pack(fill="both", expand=True)

    def on_horse_select(self, event):
        selection = self.horse_list.curselection()
        if not selection:
            return

        index = selection[0]
        self.selected_horse = self.data["horses"][index]

        image_path = self.selected_horse["image"]
        if os.path.exists(image_path):
            img = Image.open(image_path)
            img = img.resize((200, 200))
            self.image_cache = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.image_cache)

    def check_updates(self):
        def run():
            self.progress.start()
            crawl_horses()
            crawl_support_cards()
            self.data = load_data()
            self.progress.stop()
            messagebox.showinfo("Update", "Update scan complete.")

        threading.Thread(target=run).start()

    def show_recommendations(self):
        if not self.selected_horse:
            messagebox.showwarning("Select Horse", "Please select a horse first.")
            return

        self.recommend_box.delete(0, "end")

        recommendations = recommend_cards(self.selected_horse["name"], self.data)

        for card in recommendations:
            self.recommend_box.insert("end", card["name"])

    def blacklist_card(self):
        selection = self.recommend_box.curselection()
        if not selection:
            return

        card_name = self.recommend_box.get(selection[0])

        if card_name not in self.data["blacklist"]:
            self.data["blacklist"].append(card_name)
            save_data(self.data)

        messagebox.showinfo("Blacklisted", f"{card_name} added to blacklist.")

    def run(self):
        self.root.mainloop()
