import requests

BASE = "https://umamusume.run"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_all(progress_callback=None):

    horses = []
    cards = []

    try:
        response = requests.get(f"{BASE}/database", headers=HEADERS, timeout=20)
        data = response.json()
        for item in data.get("characters", []):
            horses.append({
                "name": item.get("name"),
                "source": "umamusume_run"
            })
    except:
        pass

    try:
        response = requests.get(f"{BASE}/database/support-cards", headers=HEADERS, timeout=20)
        data = response.json()
        for item in data.get("cards", []):
            cards.append({
                "name": item.get("name"),
                "source": "umamusume_run"
            })
    except:
        pass

    return horses, cards
