import sys
import os
import logging
import requests
import pandas as pd
from bs4 import BeautifulSoup
import PySimpleGUI as sg
from utils.fetch import fetch_horses, fetch_cards

# ----------------------------
# Logging Setup
# ----------------------------
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logging.info("Application started")

# ----------------------------
# GUI Setup
# ----------------------------
sg.theme("DarkBlue3")

layout = [
    [sg.Text("Uma Musume Helper", font=("Arial", 16))],
    [sg.Button("Update Horses & Cards", key="UPDATE")],
    [sg.Multiline("", size=(100, 20), key="OUTPUT", expand_x=True, expand_y=True)],
    [sg.Button("Exit", key="EXIT")]
]

window = sg.Window("Uma Musume Helper", layout, resizable=True)

horses_data = []
cards_data = []

# ----------------------------
# Fetch & Filter Data
# ----------------------------
def fetch_and_filter():
    global horses_data, cards_data
    try:
        horses = fetch_horses()
        cards = fetch_cards()

        # Only include "Initially released (EN)"
        horses_data = [h for h in horses if "Initially released (EN)" in h.get("release", "")]
        cards_data = [c for c in cards if "Initially released (EN)" in c.get("release", "")]

        logging.info(f"Fetched {len(horses_data)} horses and {len(cards_data)} cards (EN only).")
        return True
    except Exception as e:
        logging.warning(f"API failed, using cache. {e}")
        return False

# ----------------------------
# Event Loop
# ----------------------------
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "EXIT"):
        break

    if event == "UPDATE":
        success = fetch_and_filter()
        if success:
            output = f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.\n"
            output += "Horses (first 5):\n" + "\n".join([h['name'] for h in horses_data[:5]]) + "\n\n"
            output += "Cards (first 5):\n" + "\n".join([c['name'] for c in cards_data[:5]])
            window["OUTPUT"].update(output)
        else:
            window["OUTPUT"].update("Failed to fetch data. Check logs.")

window.close()
logging.info("Application closed")
sys.exit(0)
