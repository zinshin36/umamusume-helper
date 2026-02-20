# utils/fetch.py

import requests
from bs4 import BeautifulSoup
import json
from config import HORSES_PAGE, CARDS_PAGE, CACHE_FILE

def scrape_horses():
    """Scrape horses (trainees) with 'Initially released (EN)'"""
    try:
        r = requests.get(HORSES_PAGE)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        horses = []
        for row in soup.select("table.wikitable tr"):
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            name = cols[0].get_text(strip=True)
            release = cols[1].get_text(strip=True)
            if "Initially released (EN)" in release:
                horses.append({"name": name})
        return horses
    except Exception as e:
        print(f"Error scraping horses: {e}")
        return []

def scrape_cards():
    """Scrape support cards with 'Initially released (EN)'"""
    try:
        r = requests.get(CARDS_PAGE)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        cards = []
        for row in soup.select("table.wikitable tr"):
            cols = row.find_all("td")
            if len(cols) < 2:
                continue
            name = cols[0].get_text(strip=True)
            release = cols[1].get_text(strip=True)
            if "Initially released (EN)" in release:
                cards.append({"name": name})
        return cards
    except Exception as e:
        print(f"Error scraping cards: {e}")
        return []

def fetch_data():
    """Fetch horses and cards and save to cache.json"""
    horses = scrape_horses()
    cards = scrape_cards()
    cache = {"horses": horses, "cards": cards}
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(horses)} horses and {len(cards)} cards to cache")
    except Exception as e:
        print(f"Error saving cache: {e}")
    return cache

def load_cache():
    """Load data from cache.json"""
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        print("Cache not found or invalid, returning empty data")
        return {"horses": [], "cards": []}
