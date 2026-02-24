import tkinter as tk
from tkinter import messagebox
import threading
import crawler


def run_crawler():
    try:
        crawler.crawl()
        messagebox.showinfo("Done", "Crawl completed successfully.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def start_gui():
    root = tk.Tk()
    root.title("Umamusume Builder")
    root.geometry("300x150")

    btn = tk.Button(
        root,
        text="Start Crawl",
        command=lambda: threading.Thread(target=run_crawler).start(),
        height=2,
        width=20
    )
    btn.pack(pady=40)

    root.mainloop()
