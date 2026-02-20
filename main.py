import PySimpleGUI as sg
from utils import fetch, recommend

# Fetch initial data
horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()

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
        break
    elif event == "Update Data":
        horses_data, cards_data = fetch.fetch_horses(), fetch.fetch_cards()
        sg.popup("Data Updated!")
    elif event == "Add to Blacklist":
        recommend.blacklist.add(values["-BLACK-"])
        sg.popup(f"Blacklisted: {values['-BLACK-']}")
    elif event == "Recommend":
        horse_name = values["-HORSE-"]
        window["-RACES-"].update(", ".join(recommend.recommend_races(horse_name, horses_data)))
        deck = recommend.build_deck(horse_name, horses_data, cards_data)
        # Format deck for display
        deck_display = [f"{c['name']} ({c['type']}, {c.get('rarity','N/A')})" for c in deck]
        window["-DECK-"].update(deck_display)

window.close()
