import os
import logging
import PySimpleGUI as sg
from utils import fetch, recommend

# ---- LOGGING ----
if not os.path.exists("logs"):
    os.makedirs("logs")

logging.basicConfig(
    filename="logs/log.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# ---- FETCH INITIAL DATA ----
horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()
logging.info("Fetched initial horse/card data successfully")

# Base horse names (without versions)
base_horse_names = sorted(list({h['name'].split('[')[0].strip() for h in horses_data}))

# ---- GUI LAYOUT ----
layout = [
    [sg.Button("Update Horses & Cards")],
    [sg.Text("Select Horse:")],
    [sg.Combo(values=base_horse_names, key="-HORSEBASE-", enable_events=True, size=(50,1))],
    [sg.Text("Select Version:")],
    [sg.Combo(values=[], key="-HORSEVERSION-", enable_events=True, size=(50,1))],
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
            base_horse_names = sorted(list({h['name'].split('[')[0].strip() for h in horses_data}))
            window["-HORSEBASE-"].update(values=base_horse_names)
            sg.popup("Horses and Cards Updated!")
            logging.info("Horses and cards updated successfully")
        except Exception as e:
            logging.exception(f"Error updating data: {e}")

    elif event == "-HORSEBASE-":
        base_name = values["-HORSEBASE-"]
        versions = [h['name'] for h in horses_data if h['name'].startswith(base_name)]
        window["-HORSEVERSION-"].update(values=versions, value=versions[0] if versions else "")
        if versions:
            selected_horse = recommend.find_horse(versions[0], horses_data)[0]
            window["-RACES-"].update(", ".join(recommend.recommend_races(selected_horse)))
            deck = recommend.build_deck(selected_horse, cards_data)
            deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
            window["-DECK-"].update(deck_display)
            logging.info(f"Selected horse: {selected_horse['name']}, deck: {deck_display}")

    elif event == "-HORSEVERSION-":
        if values["-HORSEVERSION-"]:
            version_name = values["-HORSEVERSION-"]
            matches = recommend.find_horse(version_name, horses_data)
            if matches:
                selected_horse = matches[0]
                window["-RACES-"].update(", ".join(recommend.recommend_races(selected_horse)))
                deck = recommend.build_deck(selected_horse, cards_data)
                deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
                window["-DECK-"].update(deck_display)
                logging.info(f"Selected horse version: {selected_horse['name']}, deck: {deck_display}")

    elif event == "Add to Blacklist":
        if values["-BLACK-"]:
            recommend.blacklist.add(values["-BLACK-"])
            sg.popup(f"Blacklisted: {values['-BLACK-']}")
            logging.info(f"Added to blacklist: {values['-BLACK-']}")
            if selected_horse:
                deck = recommend.build_deck(selected_horse, cards_data)
                deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
                window["-DECK-"].update(deck_display)

window.close()
