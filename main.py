# main.py

import sys
import logging
import PySimpleGUI as sg
from utils import fetch

# ----------------------------
# Logging Setup
# ----------------------------
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
    [sg.Text("Uma Musume Helper (Global EN)", font=("Arial", 16))],
    [sg.Button("Load Data", key="LOAD"), sg.Button("Update Data", key="UPDATE"), sg.Button("Exit", key="EXIT")],
    [sg.Multiline(size=(100, 25), key="OUTPUT", expand_x=True, expand_y=True)]
]

window = sg.Window("Uma Musume Helper", layout, resizable=True)

# ----------------------------
# Event Loop
# ----------------------------
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, "EXIT"):
        break

    if event == "LOAD":
        data = fetch.load_cache()
        horses = data.get("horses", [])
        cards = data.get("cards", [])
        output = f"Horses ({len(horses)}):\n" + "\n".join(h['name'] for h in horses[:20])
        output += f"\n\nSupport Cards ({len(cards)}):\n" + "\n".join(c['name'] for c in cards[:20])
        window["OUTPUT"].update(output)
        logging.info("Loaded data from cache")

    if event == "UPDATE":
        window["OUTPUT"].update("Fetching latest data from Wiki...")
        data = fetch.fetch_data()
        horses = data.get("horses", [])
        cards = data.get("cards", [])
        output = f"Horses ({len(horses)}):\n" + "\n".join(h['name'] for h in horses[:20])
        output += f"\n\nSupport Cards ({len(cards)}):\n" + "\n".join(c['name'] for c in cards[:20])
        window["OUTPUT"].update(output)
        logging.info("Fetched latest data from Wiki")

window.close()
logging.info("Application closed")
sys.exit(0)
