import sys
import logging
import requests
import pandas as pd
import tkinter as tk
from tkinter import scrolledtext


# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")


# ----------------------------
# Fetch Data
# ----------------------------
def fetch_initial_data():
    try:
        response = requests.get("https://jsonplaceholder.typicode.com/posts")
        response.raise_for_status()
        data = response.json()

        df = pd.DataFrame(data)
        logging.info("Fetched initial data successfully")

        return df

    except Exception as e:
        logging.error(f"Error fetching data: {e}")
        return None


# ----------------------------
# GUI (tkinter - stable)
# ----------------------------
def load_data():
    df = fetch_initial_data()

    output_text.delete("1.0", tk.END)

    if df is not None:
        output_text.insert(tk.END, df.head().to_string())
    else:
        output_text.insert(tk.END, "Failed to fetch data. Check logs.")


root = tk.Tk()
root.title("Uma Musume Helper")
root.geometry("800x600")

title_label = tk.Label(root, text="Horse/Card Data Viewer", font=("Arial", 16))
title_label.pack(pady=10)

button_frame = tk.Frame(root)
button_frame.pack(pady=5)

load_button = tk.Button(button_frame, text="Load Data", command=load_data)
load_button.pack(side=tk.LEFT, padx=5)

exit_button = tk.Button(button_frame, text="Exit", command=root.destroy)
exit_button.pack(side=tk.LEFT, padx=5)

output_text = scrolledtext.ScrolledText(root, width=95, height=25)
output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()

logging.info("Application closed")
sys.exit(0)
