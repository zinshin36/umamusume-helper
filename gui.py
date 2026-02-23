import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from crawler import crawl_all
from data_manager import load_data, save_data


class App:

    def __init__(self, root):
        self.root = root
        root.title("Umamusume Helper")
        root.geometry("900x600")

        self.progress = ttk.Progressbar(root, length=400)
        self.progress.pack(pady=5)

        self.status = tk.Label(root, text="Ready")
        self.status.pack()

        tk.Button(root, text="Update Database", command=self.update_db).pack(pady=5)

        frame = tk.Frame(root)
        frame.pack(fill="both", expand=True)

        # Horse list
        self.horse_list = tk.Listbox(frame, width=40)
        self.horse_list.pack(side="left", fill="both", expand=True)
        self.horse_list.bind("<<ListboxSelect>>", self.show_horse)

        # Support list
        self.card_list = tk.Listbox(frame, width=40)
        self.card_list.pack(side="left", fill="both", expand=True)

        # Image preview
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        self.load_lists()

    def update_progress(self, percent, message):
        self.progress["value"] = percent
        self.status.config(text=f"{percent}% - {message}")
        self.root.update_idletasks()

    def update_db(self):
        crawl_all(self.update_progress)
        self.load_lists()

    def load_lists(self):
        data = load_data()

        self.horse_list.delete(0, tk.END)
        self.card_list.delete(0, tk.END)

        for h in data["horses"]:
            self.horse_list.insert(tk.END, h["name"])

        for c in data["cards"]:
            self.card_list.insert(tk.END, c["name"])

    def show_horse(self, event):
        selection = self.horse_list.curselection()
        if not selection:
            return

        index = selection[0]
        data = load_data()
        horse = data["horses"][index]

        img = Image.open(horse["image"])
        img = img.resize((200, 200))
        photo = ImageTk.PhotoImage(img)

        self.image_label.config(image=photo)
        self.image_label.image = photo


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()
