import os
import time
import requests
from bs4 import BeautifulSoup
from utils.merge import slugify

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_CHARACTER_URL = "https://gametora.com/umamusume/characters"
BASE_SUPPORT_URL = "https://gametora.com/umamusume/supports"

def safe_get(url):
    time.sleep(0.4)
    return requests.get(url, headers=HEADERS, timeout=15)

def download_image(url, path):
    try:
        r = requests.get(url, headers=HEADERS)
        with open(path, "wb") as f:
            f.write(r.content)
    except:
        pass

def fetch_characters(progress_callback=None):
    characters = []
    os.makedirs("images/characters", exist_ok=True)

    r = safe_get(BASE_CHARACTER_URL)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("a.character-card")
    total = len(cards)

    for i, card in enumerate(cards):
        name = card.get("title")
        img = card.select_one("img")
        img_url = img["src"] if img else None

        char_id = slugify(name)

        image_path = None
        if img_url:
            image_path = f"images/characters/{char_id}.png"
            if not os.path.exists(image_path):
                download_image(img_url, image_path)

        characters.append({
            "id": char_id,
            "name": name,
            "versions": [],
            "images": [image_path] if image_path else [],
            "sources": ["GameTora"]
        })

        if progress_callback:
            progress_callback(int((i/total)*50))

    return characters

def fetch_support_cards(progress_callback=None):
    cards_data = []
    os.makedirs("images/support_cards", exist_ok=True)

    r = safe_get(BASE_SUPPORT_URL)
    soup = BeautifulSoup(r.text, "lxml")

    cards = soup.select("a.support-card")
    total = len(cards)

    for i, card in enumerate(cards):
        name = card.get("title")
        rarity = "SSR" if "SSR" in name else "SR"

        card_id = slugify(name) + "-" + rarity.lower()

        img = card.select_one("img")
        img_url = img["src"] if img else None

        image_path = None
        if img_url:
            image_path = f"images/support_cards/{card_id}.png"
            if not os.path.exists(image_path):
                download_image(img_url, image_path)

        cards_data.append({
            "id": card_id,
            "name": name,
            "rarity": rarity,
            "type": "Unknown",
            "bonuses": {},
            "skills": [],
            "images": [image_path] if image_path else [],
            "sources": ["GameTora"]
        })

        if progress_callback:
            progress_callback(50 + int((i/total)*50))

    return cards_data

def fetch_all(progress_callback=None):
    characters = fetch_characters(progress_callback)
    supports = fetch_support_cards(progress_callback)

    if progress_callback:
        progress_callback(100)

    return characters, supports
