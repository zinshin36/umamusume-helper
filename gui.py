import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from utils.fetch import fetch_all_sites
from utils.storage import load_data, setup_logging


class App:

    def __init__(self, root):
        setup_logging()

        self.root = root
        root.title("Umamusume Builder")
        root.geometry("500x600")

        tk.Label(root, text="Umamusume Database Builder", font=("Arial", 16)).pack(pady=10)

        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack()

        self.progress = ttk.Progressbar(root, length=400)
        self.progress.pack(pady=5)

        self.count_label = tk.Label(root, text="Horses: 0 | Cards: 0")
        self.count_label.pack(pady=5)

        self.image_label = tk.Label(root)
        self.image_label.pack(pady=10)

        tk.Button(root, text="Crawl Database", command=self.start_crawl, width=20).pack(pady=10)

        self.refresh_counts()

    def update_progress(self, percent, message):
        self.progress["value"] = percent
        self.status_label.config(text=f"{percent}% - {message}")
        self.root.update_idletasks()

    def refresh_counts(self):
        data = load_data()
        horses = len(data["horses"])
        cards = len(data["cards"])
        self.count_label.config(text=f"Horses: {horses} | Cards: {cards}")

        if horses > 0:
            img_path = data["horses"][0]["image"]
            if img_path and os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((200, 200))
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo)
                self.image_label.image = photo

    def start_crawl(self):
        horses, cards = fetch_all_sites(self.update_progress)
        self.refresh_counts()


def run():
    root = tk.Tk()
    App(root)
    root.mainloop()
