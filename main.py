import sys
import os
import logging
import PySimpleGUI as sg
from utils.fetch import fetch_data
from utils.recommend import recommend_inheritance

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
sg.theme("DarkBlue")

layout = [
    [sg.Text("Uma Musume Helper (EN Wiki)", font=("Arial", 16))],
    [sg.Button("Update Horses & Cards", key="UPDATE")],
    [sg.Text("Select Horse:")],
    [sg.Combo([], key="HORSE_SELECT", size=(40, 1))],
    [sg.Button("Recommend Inheritance", key="INHERIT")],
    [sg.Multiline("", size=(100, 20), key="OUTPUT", expand_x=True, expand_y=True)],
    [sg.Button("Exit", key="EXIT")]
]

window = sg.Window("Uma Musume Helper", layout, resizable=True)

horses_data = []
cards_data = []

while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "EXIT"):
        break

    if event == "UPDATE":
        data = fetch_data()
        horses_data = data.get("horses", [])
        cards_data = data.get("cards", [])

        horse_names = [h['name'] for h in horses_data]
        window["HORSE_SELECT"].update(values=horse_names)

        logging.info(f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.")

        window["OUTPUT"].update(
            f"Loaded {len(horses_data)} horses and {len(cards_data)} cards.\n"
            "Select a horse and click Recommend Inheritance."
        )

    if event == "INHERIT":
        selected = values.get("HORSE_SELECT")
        if not selected:
            window["OUTPUT"].update("Please select a horse first.")
            continue

        result = recommend_inheritance(selected, horses_data)

        window["OUTPUT"].update(result)

window.close()
logging.info("Application closed")
sys.exit(0)
