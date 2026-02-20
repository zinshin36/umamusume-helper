import os
import logging
import PySimpleGUI as sg
from utils import fetch, recommend

# ---- SETUP LOGGING ----
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# ---- FETCH DATA ----
try:
    horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()
    logging.info("Fetched initial horse/card data successfully")
except Exception as e:
    logging.exception(f"Failed to fetch initial data: {e}")

# ---- GUI LAYOUT ----
layout = [
    [sg.Text("Horse Name:"), sg.Input(key="-HORSE-"), sg.Button("Recommend")],
    [sg.Text("Recommended Races:"), sg.Text("", key="-RACES-")],
    [sg.Text("Recommended Support Deck (Top 6):")],
    [sg.Listbox(values=[], size=(50,10), key="-DECK-")],
    [sg.Text("Blacklist Card:"), sg.Input(key="-BLACK-"), sg.Button("Add to Blacklist")],
    [sg.Button("Update Data")]
]

window = sg.Window("Uma Musume Helper", layout)

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        logging.info("Application closed by user")
        break
    elif event == "Update Data":
        try:
            horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()
            sg.popup("Data Updated!")
            logging.info("Data updated successfully")
        except Exception as e:
            logging.exception(f"Error updating data: {e}")
    elif event == "Add to Blacklist":
        recommend.blacklist.add(values["-BLACK-"])
        sg.popup(f"Blacklisted: {values['-BLACK-']}")
        logging.info(f"Added to blacklist: {values['-BLACK-']}")
    elif event == "Recommend":
        try:
            horse_name = values["-HORSE-"]
            window["-RACES-"].update(", ".join(recommend.recommend_races(horse_name, horses_data)))
            deck = recommend.build_deck(horse_name, horses_data, cards_data)
            deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
            window["-DECK-"].update(deck_display)
            logging.info(f"Recommended deck for {horse_name}: {deck_display}")
        except Exception as e:
            logging.exception(f"Error generating recommendation for {values['-HORSE-']}: {e}")

window.close()
