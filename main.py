import os
import sys
import logging
import threading
import traceback
import PySimpleGUI as sg

from utils.fetch import fetch_all_data

# =========================
# PATH + LOGGING SETUP
# =========================

def get_base_path():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

BASE_PATH = get_base_path()
LOG_DIR = os.path.join(BASE_PATH, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "app.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")

# =========================
# UPDATE THREAD
# =========================

def update_data_thread(window):
    try:
        logging.info("Starting data update...")
        window.write_event_value("-STATUS-", "Fetching data...")

        horses, cards = fetch_all_data()

        logging.info(f"Fetched {len(horses)} horses and {len(cards)} cards.")

        window.write_event_value("-UPDATE_DONE-", (horses, cards))

    except Exception:
        logging.error("Update failed:")
        logging.error(traceback.format_exc())
        window.write_event_value("-ERROR-", "Update failed. Check logs.")

def start_update(window):
    threading.Thread(
        target=update_data_thread,
        args=(window,),
        daemon=True
    ).start()

# =========================
# GUI
# =========================

layout = [
    [sg.Button("Update Data")],
    [sg.Text("Status: Idle", key="-STATUS-")],
]

window = sg.Window("Umamusume Builder", layout)

while True:
    event, values = window.read()

    if event == sg.WINDOW_CLOSED:
        break

    if event == "Update Data":
        start_update(window)

    if event == "-STATUS-":
        window["-STATUS-"].update(f"Status: {values}")

    if event == "-UPDATE_DONE-":
        horses, cards = values
        window["-STATUS-"].update(
            f"Loaded {len(horses)} horses and {len(cards)} cards."
        )

    if event == "-ERROR-":
        sg.popup_error(values)

window.close()
