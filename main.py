import sys
import os
import logging
import PySimpleGUI as sg
from utils.fetch import fetch_data

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
    [sg.Text("Uma Musume Helper (EN Wiki)", font=("Arial", 16))],
    [sg.Button("Update Horses & Cards", key="UPDATE")],
    [sg.Multiline("", size=(100, 20), key="OUTPUT", expand_x=True, expand_y=True)],
    [sg.Button("Exit", key="EXIT")]
]

window = sg.Window("Uma Musume Helper", layout, resizable=True)

horses_data = []
cards_data = []

# ----------------------------
# Event Loop
# ----------------------------
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "EXIT"):
        break

    if event == "UPDATE":
        data = fetch_data()
        horses_data = data.get("horses", [])
        cards_data = data.get("cards", [])

        logging.info(f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.")

        if horses_data and cards_data:
            output = f"Horses (first 5):\n" + "\n".join([h['name'] for h in horses_data[:5]]) + "\n\n"
            output += "Cards (first 5):\n" + "\n".join([c['name'] for c in cards_data[:5]])
            window["OUTPUT"].update(output)
        else:
            window["OUTPUT"].update("Failed to fetch data. Check logs.")

window.close()
logging.info("Application closed")
sys.exit(0)
