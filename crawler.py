import requests
import time
import logging
import json

API_BASE = "https://umapyoi.net/api/v1"
RATE_DELAY = 0.15  # ~6-7 requests per second (safe under limit)


def fetch_json(url: str):
    try:
        logging.info(f"Fetching API: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"API fetch failed '{url}': {e}")
        return None


def crawl():
    logging.info("Starting API crawl")

    # Fetch horses
    horses_url = f"{API_BASE}/character"
    horses = fetch_json(horses_url) or []
    time.sleep(RATE_DELAY)

    # Fetch support cards
    cards_url = f"{API_BASE}/support"
    cards = fetch_json(cards_url) or []
    time.sleep(RATE_DELAY)

    result = {
        "horses": horses,
        "cards": cards
    }

    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logging.error(f"Failed to write data.json: {e}")

    horse_count = len(horses)
    card_count = len(cards)

    logging.info(f"Crawl complete. Horses: {horse_count} Cards: {card_count}")

    return horse_count, card_count
