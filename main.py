import sys
import logging
import requests
import pandas as pd
import PySimpleGUI as sg


# ----------------------------
# Logging Setup
# ----------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.info("Application started")


# ----------------------------
# Example Data Fetch Function
# ----------------------------
def fetch_initial_data():
    try:
        # Replace with your actual API or data source
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
# GUI Layout (PySimpleGUI 4.60.4 Compatible)
# ----------------------------
layout = [
    [sg.Text("Horse/Card Data Viewer", font=("Arial", 14))],
    [sg.Button("Load Data"), sg.Button("Exit")],
    [sg.Multiline(size=(80, 20), key="OUTPUT")]
]

window = sg.Window("My Application", layout)


# ----------------------------
# Main Event Loop
# ----------------------------
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED or event == "Exit":
        break

    if event == "Load Data":
        df = fetch_initial_data()

        if df is not None:
            window["OUTPUT"].update(df.head().to_string())
        else:
            window["OUTPUT"].update("Failed to fetch data. Check logs.")


window.close()
logging.info("Application closed")
sys.exit(0)
