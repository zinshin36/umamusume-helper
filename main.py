import tkinter as tk
from tkinter import ttk
import threading

from utils.fetch import fetch_all_data


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Musume Helper")

        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack(pady=5)

        self.progress = ttk.Progressbar(root, length=400, maximum=100)
        self.progress.pack(pady=5)

        self.button = tk.Button(root, text="Start Crawl", command=self.start_crawl)
        self.button.pack(pady=10)

        self.result_label = tk.Label(root, text="")
        self.result_label.pack(pady=10)

    def update_progress(self, message):
        self.status_label.config(text=message)

        if "%" in message:
            try:
                percent = int(message.split("%")[0].split()[-1])
                self.progress["value"] = percent
            except:
                pass

        self.root.update_idletasks()

    def start_crawl(self):
        self.button.config(state="disabled")
        thread = threading.Thread(target=self.run_crawl)
        thread.start()

    def run_crawl(self):
        horses, cards = fetch_all_data(progress_callback=self.update_progress)

        self.result_label.config(
            text=f"Horses: {len(horses)} | Cards: {len(cards)}"
        )

        self.button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
