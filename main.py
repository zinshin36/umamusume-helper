import tkinter as tk
from tkinter import ttk
import threading

from utils.fetch import fetch_all_sites
from utils.logger import logger


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Crawler")

        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack(pady=5)

        self.progress = ttk.Progressbar(root, length=400)
        self.progress.pack(pady=5)

        self.button = tk.Button(root, text="Start Crawl", command=self.start_crawl)
        self.button.pack(pady=10)

    def update_progress(self, message):
        self.status_label.config(text=message)

        # Extract percent if present
        if "%" in message:
            percent = int(message.split("%")[0].split()[-1])
            self.progress["value"] = percent

        self.root.update_idletasks()

    def start_crawl(self):
        thread = threading.Thread(target=self.run_crawl)
        thread.start()

    def run_crawl(self):
        logger.info("Starting crawl")

        horses, cards = fetch_all_sites(progress_callback=self.update_progress)

        logger.info("Crawl complete")
        logger.info(f"Horses: {len(horses)}")
        logger.info(f"Cards: {len(cards)}")

        self.update_progress("Crawl complete")


root = tk.Tk()
app = App(root)
root.mainloop()
