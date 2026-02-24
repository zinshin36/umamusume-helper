import tkinter as tk
from tkinter import ttk
import threading
import crawler


def start_gui():
    app = App()
    app.mainloop()


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Umamusume Database Builder")
        self.geometry("500x300")

        self.progress = ttk.Progressbar(self, length=400)
        self.progress.pack(pady=10)

        self.status_label = tk.Label(self, text="Idle")
        self.status_label.pack()

        self.count_label = tk.Label(self, text="Horses: 0 | Cards: 0")
        self.count_label.pack(pady=5)

        self.update_button = tk.Button(
            self,
            text="Update Database (API)",
            command=lambda: threading.Thread(target=self.run_update).start()
        )
        self.update_button.pack(pady=20)

    def run_update(self):
        self.status_label.config(text="Updating from API...")
        horses, cards = crawler.crawl()
        self.count_label.config(text=f"Horses: {horses} | Cards: {cards}")
        self.status_label.config(text="Update Complete!")
