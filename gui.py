import threading
import os
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

from api import UmaAPI
from data_manager import DataManager
from optimizer import DeckOptimizer


class UmaGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Uma Musume Deck Builder")
        self.root.geometry("1100x700")

        self.data_manager = DataManager()
        self.horses, self.supports = self.data_manager.load()

        self.optimizer = DeckOptimizer()

        self.selected_horse = None
        self.support_images = {}

        self.build_ui()
        self.refresh_horse_list()

    # ================= UI =================

    def build_ui(self):

        top_frame = ttk.Frame(self.root)
        top_frame.pack(fill="x", padx=10, pady=5)

        self.update_btn = ttk.Button(top_frame, text="Update Database", command=self.update_database)
        self.update_btn.pack(side="left")

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(top_frame, textvariable=self.status_var)
        self.status_label.pack(side="left", padx=10)

        self.progress = ttk.Progressbar(top_frame, length=250)
        self.progress.pack(side="left", padx=10)

        # -------- LEFT PANEL --------

        left_frame = ttk.Frame(self.root)
        left_frame.pack(side="left", fill="y", padx=10)

        ttk.Label(left_frame, text="Horses").pack()

        self.horse_listbox = tk.Listbox(left_frame, height=25, width=30)
        self.horse_listbox.pack()
        self.horse_listbox.bind("<<ListboxSelect>>", self.on_horse_select)

        # -------- RIGHT PANEL --------

        right_frame = ttk.Frame(self.root)
        right_frame.pack(side="right", fill="both", expand=True, padx=10)

        self.horse_info = ttk.Label(right_frame, text="Select a horse", justify="left")
        self.horse_info.pack(anchor="w")

        ttk.Button(right_frame, text="Optimize Deck", command=self.optimize_deck).pack(pady=5)

        self.result_frame = ttk.Frame(right_frame)
        self.result_frame.pack(fill="both", expand=True)

    # ================= DATABASE UPDATE =================

    def update_database(self):

        self.status_var.set("Connecting to API...")
        self.progress["value"] = 0
        self.update_btn.config(state="disabled")

        thread = threading.Thread(target=self._update_database_thread)
        thread.start()

    def _update_database_thread(self):

        try:
            api = UmaAPI()

            self.set_status("Fetching Horses...", 10)
            horses = api.fetch_all_horses()

            self.set_status("Fetching Supports...", 50)
            supports = api.fetch_all_supports()

            self.set_status("Saving Data...", 90)
            self.data_manager.save(horses, supports)

            self.horses = horses
            self.supports = supports

            self.set_status("Database Updated", 100)

            self.root.after(0, self.refresh_horse_list)

        except Exception as e:
            self.set_status("Error")
            messagebox.showerror("Error", str(e))

        finally:
            self.root.after(0, lambda: self.update_btn.config(state="normal"))

    def set_status(self, text, progress=None):
        self.root.after(0, lambda: self.status_var.set(text))
        if progress is not None:
            self.root.after(0, lambda: self.progress.configure(value=progress))

    # ================= HORSE LIST =================

    def refresh_horse_list(self):

        self.horse_listbox.delete(0, tk.END)

        for horse in self.horses:
            self.horse_listbox.insert(tk.END, horse["name"])

    def on_horse_select(self, event):

        selection = self.horse_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        self.selected_horse = self.horses[index]

        self.display_horse_info()

    def display_horse_info(self):

        horse = self.selected_horse

        growth = horse.get("growth", {})
        strategy = horse.get("strategy", "Unknown")

        text = (
            f"Name: {horse['name']}\n"
            f"Strategy: {strategy}\n\n"
            f"Growth Rates:\n"
            f"Speed: {growth.get('Speed', 0)}\n"
            f"Stamina: {growth.get('Stamina', 0)}\n"
            f"Power: {growth.get('Power', 0)}\n"
            f"Guts: {growth.get('Guts', 0)}\n"
            f"Wisdom: {growth.get('Wisdom', 0)}"
        )

        self.horse_info.config(text=text)

    # ================= OPTIMIZER =================

    def optimize_deck(self):

        if not self.selected_horse:
            messagebox.showwarning("Select Horse", "Please select a horse first.")
            return

        for widget in self.result_frame.winfo_children():
            widget.destroy()

        best_deck = self.optimizer.optimize(self.selected_horse, self.supports)

        row = 0

        for support in best_deck:

            frame = ttk.Frame(self.result_frame)
            frame.grid(row=row, column=0, pady=5, sticky="w")

            image_label = ttk.Label(frame)
            image_label.pack(side="left")

            self.load_image(
                support.get("image"),
                image_label,
                fallback_text=f"{support['name']} ({support['type']})"
            )

            info_text = (
                f"{support['name']} ({support['rarity']})\n"
                f"Type: {support['type']}\n"
                f"Bonuses: {support['stat_bonus']}"
            )

            ttk.Label(frame, text=info_text, justify="left").pack(side="left", padx=10)

            row += 1

    # ================= IMAGE HANDLING =================

    def load_image(self, path, label_widget, fallback_text):

        if path and os.path.exists(path):
            try:
                img = Image.open(path)
                img = img.resize((120, 160))
                photo = ImageTk.PhotoImage(img)
                label_widget.config(image=photo, text="")
                label_widget.image = photo
                return
            except:
                pass

        label_widget.config(text=fallback_text, image="")


# ================= START APP =================

def start_app():
    root = tk.Tk()
    app = UmaGUI(root)
    root.mainloop()
