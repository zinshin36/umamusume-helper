import tkinter as tk
from tkinter import ttk
import threading
import crawler

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Umamusume Builder")
        self.geometry("500x300")

        self.progress = ttk.Progressbar(self, length=400)
        self.progress.pack(pady=10)

        self.status_label = tk.Label(self, text="Idle")
        self.status_label.pack()

        self.count_label = tk.Label(self, text="Horses: 0 | Cards: 0")
        self.count_label.pack(pady=5)

        self.btn = tk.Button(
            self,
            text="Update Database (API)",
            command=lambda: threading.Thread(target=self.start_crawl).start()
        )
        self.btn.pack(pady=20)

    def start_crawl(self):
        self.status_label.config(text="Crawling API…")
        horses, cards = crawler.crawl()
        self.count_label.config(text=f"Horses: {horses} | Cards: {cards}")
        self.status_label.config(text="Crawl complete!")
