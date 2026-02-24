import requests
import json
import os
import time
import logging
from scraper import get_global_character_names, get_global_support_names

API_BASE = "https://umapyoi.net/api/v1"
DATA_DIR = "data"
IMAGE_DIR = os.path.join(DATA_DIR, "images")
HORSE_IMG_DIR = os.path.join(IMAGE_DIR, "horses")
CARD_IMG_DIR = os.path.join(IMAGE_DIR, "support_cards")

RATE_DELAY = 0.2


def ensure_dirs():
    os.makedirs(HORSE_IMG_DIR, exist_ok=True)
    os.makedirs(CARD_IMG_DIR, exist_ok=True)


def fetch(url):
    r = requests.get(url)
    r.raise_for_status()
    return r.json()


def download_image(url, path):
    if not url:
        return
    if os.path.exists(path):
        return
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)


def crawl():
    logging.info("Starting API crawl")
    ensure_dirs()

    api_horses = fetch(f"{API_BASE}/character")
    api_cards = fetch(f"{API_BASE}/support")

    global_horses = get_global_character_names()
    global_cards = get_global_support_names()

    filtered_horses = []
    filtered_cards = []

    # HORSES
    for h in api_horses:
        name = h.get("name", "").lower()
        if name in global_horses:
            img = h.get("image")
            img_path = os.path.join(HORSE_IMG_DIR, f"{h['id']}.png")
            download_image(img, img_path)
            time.sleep(RATE_DELAY)

            filtered_horses.append({
                "id": h["id"],
                "name": h["name"],
                "rarity": h.get("rarity"),
                "image": img_path
            })

    # SUPPORT CARDS
    seen = set()

    for c in api_cards:
        name = c.get("name", "").lower()
        card_type = c.get("type", "")
        key = f"{name}-{card_type}"

        if name in global_cards and key not in seen:
            seen.add(key)

            img = c.get("image")
            img_path = os.path.join(CARD_IMG_DIR, f"{c['id']}.png")
            download_image(img, img_path)
            time.sleep(RATE_DELAY)

            filtered_cards.append({
                "id": c["id"],
                "name": c["name"],
                "rarity": c.get("rarity"),
                "type": card_type,
                "stats": c.get("stats", {}),
                "image": img_path
            })

    result = {
        "horses": filtered_horses,
        "cards": filtered_cards
    }

    with open(os.path.join(DATA_DIR, "data.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(filtered_horses)} Cards: {len(filtered_cards)}")
