import requests
import time
import logging
import json

API_BASE = "https://umapyoi.net/api/v1"

# Respect the API rate limits!
# 10 req/sec, 500 req/min
# We'll use a delay to stay safe.
RATE_DELAY = 0.12  # ~8 calls per second

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_json(url: str):
    try:
        logging.info(f"Fetching API: {url}")
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        logging.error(f"API fetch failed '{url}': {e}")
        return None


def fetch_all_horses():
    url = f"{API_BASE}/character"
    data = fetch_json(url)
    if not data:
        return []
    return data  # depends on API response shape


def fetch_all_support_cards():
    url = f"{API_BASE}/support"
    data = fetch_json(url)
    if not data:
        return []
    return data  # depends on API response shape


def crawl():
    logging.info("Starting API crawl")

    horses = fetch_all_horses()
    time.sleep(RATE_DELAY)

    cards = fetch_all_support_cards()
    time.sleep(RATE_DELAY)

    # Save locally
    result = {
        "horses": horses or [],
        "cards": cards or []
    }

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    horse_count = len(result["horses"])
    card_count = len(result["cards"])

    logging.info(f"API Crawl complete. Horses: {horse_count} Cards: {card_count}")

    return horse_count, card_count
