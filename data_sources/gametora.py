import requests

BASE = "https://gametora.com/umamusume"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_all(progress_callback=None):

    horses = []
    cards = []

    try:
        response = requests.get(BASE, headers=HEADERS, timeout=20)
        data = response.json()

        for item in data.get("characters", []):
            horses.append({
                "name": item.get("name"),
                "source": "gametora"
            })

        for item in data.get("support_cards", []):
            cards.append({
                "name": item.get("name"),
                "source": "gametora"
            })

    except:
        pass

    return horses, cards
