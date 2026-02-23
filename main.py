import tkinter as tk
from tkinter import ttk
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO

from utils.fetch import fetch_all_data


class App:

    def __init__(self, root):
        self.root = root
        self.root.title("Uma Musume Helper")

        self.status_label = tk.Label(root, text="Ready")
        self.status_label.pack()

        self.progress = ttk.Progressbar(root, length=400, maximum=100)
        self.progress.pack()

        self.button = tk.Button(root, text="Start Crawl", command=self.start)
        self.button.pack()

        self.canvas = tk.Canvas(root, height=400)
        self.canvas.pack(fill="both", expand=True)

        self.frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.frame, anchor="nw")

        self.images = []

    def update_progress(self, message):
        self.status_label.config(text=message)

        if "%" in message:
            try:
                percent = int(message.split("%")[0].split()[-1])
                self.progress["value"] = percent
            except:
                pass

        self.root.update_idletasks()

    def start(self):
        threading.Thread(target=self.run).start()

    def run(self):
        horses, cards = fetch_all_data(progress_callback=self.update_progress)

        row = 0
        for item in horses[:10] + cards[:10]:
            if item.get("image"):
                try:
                    response = requests.get(item["image"], timeout=10)
                    img = Image.open(BytesIO(response.content))
                    img = img.resize((64, 64))
                    photo = ImageTk.PhotoImage(img)
                    label = tk.Label(self.frame, image=photo)
                    label.grid(row=row, column=0)
                    self.images.append(photo)
                except:
                    pass

            tk.Label(self.frame, text=item["name"]).grid(row=row, column=1)
            row += 1


root = tk.Tk()
app = App(root)
root.mainloop()
