import tkinter as tk
import threading
import logging
from fetch import fetch_all_data

logging.basicConfig(level=logging.INFO)


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Uma Musume Data Fetcher")
        self.root.geometry("500x200")

        self.status_label = tk.Label(root, text="Idle", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.result_label = tk.Label(root, text="", font=("Arial", 12))
        self.result_label.pack(pady=10)

        self.fetch_button = tk.Button(root, text="Start Crawl", command=self.start_fetch)
        self.fetch_button.pack(pady=10)

    def update_progress(self, message):
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def start_fetch(self):
        self.fetch_button.config(state="disabled")
        thread = threading.Thread(target=self.run_fetch)
        thread.start()

    def run_fetch(self):
        horses, cards = fetch_all_data(progress_callback=self.update_progress)

        self.status_label.config(text="Crawl Complete")
        self.result_label.config(text=f"Horses: {len(horses)} | Cards: {len(cards)}")
        self.fetch_button.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
