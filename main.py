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
horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()
logging.info("Fetched initial horse/card data successfully")

# ---- GUI LAYOUT ----
layout = [
    [sg.Button("Update Horses & Cards")],
    [sg.Text("Select Horse Version:")],
    [sg.Listbox(values=[h['name'] for h in horses_data], size=(50,10), key="-HORSES-", enable_events=True)],
    [sg.Text("Recommended Races:"), sg.Text("", key="-RACES-")],
    [sg.Text("Recommended Support Deck (Top 6):")],
    [sg.Listbox(values=[], size=(50,10), key="-DECK-")],
    [sg.Text("Blacklist Card:"), sg.Input(key="-BLACK-"), sg.Button("Add to Blacklist")]
]

window = sg.Window("Uma Musume Helper", layout)

selected_horse = None

while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED:
        logging.info("Application closed by user")
        break

    elif event == "Update Horses & Cards":
        try:
            horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()
            window["-HORSES-"].update([h['name'] for h in horses_data])
            sg.popup("Horses and Cards Updated!")
            logging.info("Horses and cards updated successfully")
        except Exception as e:
            logging.exception(f"Error updating data: {e}")

    elif event == "-HORSES-":
        # User selected a horse version from list
        if values["-HORSES-"]:
            horse_name = values["-HORSES-"][0]
            matches = recommend.find_horse(horse_name, horses_data)
            if matches:
                # For now pick the first matching version
                selected_horse = matches[0]
                window["-RACES-"].update(", ".join(recommend.recommend_races(selected_horse)))
                deck = recommend.build_deck(selected_horse, cards_data)
                deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
                window["-DECK-"].update(deck_display)
                logging.info(f"Selected horse: {selected_horse['name']}, deck: {deck_display}")

    elif event == "Add to Blacklist":
        if values["-BLACK-"]:
            recommend.blacklist.add(values["-BLACK-"])
            sg.popup(f"Blacklisted: {values['-BLACK-']}")
            logging.info(f"Added to blacklist: {values['-BLACK-']}")
            # Refresh deck if a horse is selected
            if selected_horse:
                deck = recommend.build_deck(selected_horse, cards_data)
                deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
                window["-DECK-"].update(deck_display)

window.close()
