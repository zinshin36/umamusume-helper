import requests
import time
import logging
import json
import os

API_BASE = "https://umapyoi.net/api/v1"
RATE_DELAY = 0.15  # Safe under 10 req/sec

DATA_DIR = "data"
IMAGE_DIR = os.path.join(DATA_DIR, "images")
HORSE_IMG_DIR = os.path.join(IMAGE_DIR, "horses")
CARD_IMG_DIR = os.path.join(IMAGE_DIR, "support_cards")


def ensure_dirs():
    os.makedirs(HORSE_IMG_DIR, exist_ok=True)
    os.makedirs(CARD_IMG_DIR, exist_ok=True)


def fetch_json(url: str):
    try:
        logging.info(f"Fetching API: {url}")
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"API fetch failed '{url}': {e}")
        return None


def download_image(url: str, save_path: str):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        logging.error(f"Failed downloading image {url}: {e}")


def filter_global(entries):
    """
    Filters entries to GLOBAL only.
    Umapyoi uses availability flags.
    """
    global_list = []

    for entry in entries:
        # Some entries use "availability"
        # Global usually includes "EN" region
        availability = entry.get("availability", [])
        if "EN" in availability:
            global_list.append(entry)

    return global_list


def process_horses():
    horses_url = f"{API_BASE}/character"
    horses = fetch_json(horses_url) or []
    time.sleep(RATE_DELAY)

    horses = filter_global(horses)

    processed = []

    for horse in horses:
        horse_id = horse.get("id")
        name = horse.get("name", "unknown")

        image_url = horse.get("image")  # API usually provides this
        image_path = None

        if image_url:
            filename = f"{horse_id}.png"
            image_path = os.path.join(HORSE_IMG_DIR, filename)
            download_image(image_url, image_path)
            time.sleep(RATE_DELAY)

        processed.append({
            "id": horse_id,
            "name": name,
            "rarity": horse.get("rarity"),
            "image": image_path
        })

    return processed


def process_support_cards():
    cards_url = f"{API_BASE}/support"
    cards = fetch_json(cards_url) or []
    time.sleep(RATE_DELAY)

    cards = filter_global(cards)

    processed = []

    for card in cards:
        card_id = card.get("id")
        name = card.get("name", "unknown")

        image_url = card.get("image")
        image_path = None

        if image_url:
            filename = f"{card_id}.png"
            image_path = os.path.join(CARD_IMG_DIR, filename)
            download_image(image_url, image_path)
            time.sleep(RATE_DELAY)

        processed.append({
            "id": card_id,
            "name": name,
            "rarity": card.get("rarity"),
            "type": card.get("type"),
            "image": image_path
        })

    return processed


def crawl():
    logging.info("Starting API crawl")

    ensure_dirs()

    horses = process_horses()
    cards = process_support_cards()

    result = {
        "horses": horses,
        "cards": cards
    }

    with open(os.path.join(DATA_DIR, "data.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    horse_count = len(horses)
    card_count = len(cards)

    logging.info(f"Crawl complete. Horses: {horse_count} Cards: {card_count}")

    return horse_count, card_count
