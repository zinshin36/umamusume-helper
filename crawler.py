import requests
import json
import os
import logging
from pathlib import Path

BASE = "https://umapyoi.net/api/v1"

DATA_DIR = Path("data")
IMG_DIR = DATA_DIR / "images"
HORSE_DIR = IMG_DIR / "horses"
SUPPORT_DIR = IMG_DIR / "support"
DATA_FILE = DATA_DIR / "data.json"

for d in (DATA_DIR, IMG_DIR, HORSE_DIR, SUPPORT_DIR):
    os.makedirs(d, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

TIMEOUT = 15


def safe_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            logging.error(f"HTTP {r.status_code} for {url}")
            return None
        return r.json()
    except Exception as e:
        logging.error(f"JSON failure: {url} | {e}")
        return None


def download_image(url, path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200 and r.content:
            with open(path, "wb") as f:
                f.write(r.content)
        else:
            logging.error(f"Image failed: {url}")
    except Exception as e:
        logging.error(f"Image error: {url} | {e}")


def crawl(progress_callback=None, status_callback=None):

    horses = []
    cards = []

    logging.info("Starting API crawl")

    # ==========================================================
    # CHARACTERS
    # ==========================================================

    if status_callback:
        status_callback("Fetching character list...")

    char_list = safe_json(f"{BASE}/character/list")
    if not char_list:
        logging.error("Character list failed.")
        return

    total_chars = len(char_list)

    for i, c in enumerate(char_list):
        char_id = c.get("id")
        name = c.get("name_en") or c.get("name")

        if not char_id:
            continue

        img_path = HORSE_DIR / f"{char_id}.png"

        # Fetch image URL from API
        img_api = safe_json(f"{BASE}/character/images/{char_id}")

        img_url = None
        if img_api and isinstance(img_api, list) and len(img_api) > 0:
            # First image is the main icon
            img_url = img_api[0].get("url")

        if img_url and not img_path.exists():
            download_image(img_url, img_path)

        horses.append({
            "id": char_id,
            "name": name,
            "image": str(img_path)
        })

        if progress_callback:
            progress_callback("Characters", i + 1, total_chars)

    # ==========================================================
    # SUPPORT CARDS
    # ==========================================================

    if status_callback:
        status_callback("Fetching support IDs...")

    support_list = safe_json(f"{BASE}/support")
    if not support_list:
        logging.error("Support list failed.")
        return

    total_support = len(support_list)

    for i, s in enumerate(support_list):
        support_id = s.get("id")
        if not support_id:
            continue

        detail = safe_json(f"{BASE}/support/{support_id}")
        gametora = safe_json(f"{BASE}/support/{support_id}/gametora")

        name = detail.get("name_en") if detail else None
        support_type = detail.get("type") if detail else None

        img_path = SUPPORT_DIR / f"{support_id}.png"

        img_url = None
        if gametora:
            # Gametora endpoint directly gives image URL
            img_url = gametora.get("image")

        if img_url and not img_path.exists():
            download_image(img_url, img_path)

        cards.append({
            "id": support_id,
            "name": name,
            "image": str(img_path),
            "type": support_type,
            "stats": detail.get("stats", {}) if detail else {},
            "stars": 0,
            "blacklisted": False
        })

        if progress_callback:
            progress_callback("Support Cards", i + 1, total_support)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    if status_callback:
        status_callback("Crawl complete.")
