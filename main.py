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
# Fetch Data
# ----------------------------
def fetch_initial_data():
    try:
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
# GUI (PySimpleGUI 5 Safe Version)
# ----------------------------

layout = [
    [sg.Text("Horse/Card Data Viewer", font=("Arial", 14))],
    [
        sg.Button("Load Data", key="LOAD"),
        sg.Button("Exit", key="EXIT")
    ],
    [
        sg.Multiline(
            "",
            size=(80, 20),
            key="OUTPUT",
            expand_x=True,
            expand_y=True
        )
    ]
]

window = sg.Window(
    "My Application",
    layout,
    resizable=True,
    finalize=True
)


# ----------------------------
# Event Loop
# ----------------------------
while True:
    event, values = window.read()

    if event in (sg.WIN_CLOSED, "EXIT"):
        break

    if event == "LOAD":
        df = fetch_initial_data()

        if df is not None:
            window["OUTPUT"].update(df.head().to_string())
        else:
            window["OUTPUT"].update("Failed to fetch data. Check logs.")


window.close()
logging.info("Application closed")
sys.exit(0)
