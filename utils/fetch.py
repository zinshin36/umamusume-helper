import requests
from bs4 import BeautifulSoup
import json
import os
from config import HORSES_PAGE, CARDS_PAGE, CACHE_FILE

os.makedirs("data", exist_ok=True)

def scrape_horses():
    """Scrape horses from HORSES_PAGE (EN)"""
    try:
        r = requests.get(HORSES_PAGE)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        horses = []
        for link in soup.select("li.category-page__member > a"):
            horses.append({
                "name": link.text.strip(),
                "url": link["href"],
                "release": "Initially released (EN)"
            })
        return horses
    except Exception as e:
        print(f"Error scraping horses: {e}")
        return []

def scrape_cards():
    """Scrape support cards from CARDS_PAGE (EN)"""
    try:
        r = requests.get(CARDS_PAGE)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        cards = []
        for link in soup.select("li.category-page__member > a"):
            cards.append({
                "name": link.text.strip(),
                "url": link["href"],
                "release": "Initially released (EN)"
            })
        return cards
    except Exception as e:
        print(f"Error scraping cards: {e}")
        return []

def fetch_data():
    """Fetch horses and cards, fallback to cache"""
    data = {"horses": [], "cards": []}
    try:
        data["horses"] = scrape_horses()
        data["cards"] = scrape_cards()

        # Save cache
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    except Exception as e:
        print(f"Fetching failed, trying cache: {e}")
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return data
