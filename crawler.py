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
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
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
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
    except Exception as e:
        logging.error(f"Image download failed: {url} | {e}")


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
        logging.error("Character list endpoint failed.")
        return

    total_chars = len(char_list)

    for i, c in enumerate(char_list):

        char_id = c.get("id")
        name = c.get("name_en") or c.get("name")

        if not char_id or not name:
            continue

        # Get image info
        img_info = safe_json(f"{BASE}/character/images/{char_id}")
        img_url = None

        if img_info and isinstance(img_info, list) and len(img_info) > 0:
            # Use first image entry
            img_url = img_info[0].get("image_url")

        img_path = HORSE_DIR / f"{char_id}.png"

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

    support_ids = safe_json(f"{BASE}/support")

    if not support_ids:
        logging.error("Support ID endpoint failed.")
        return

    total_support = len(support_ids)

    for i, s in enumerate(support_ids):

        support_id = s.get("id")

        if not support_id:
            continue

        if status_callback:
            status_callback(f"Fetching support {i+1}/{total_support}")

        detail = safe_json(f"{BASE}/support/{support_id}")
        if not detail:
            continue

        name = detail.get("name_en") or detail.get("name")
        support_type = detail.get("type")

        img_url = detail.get("image_url")
        img_path = SUPPORT_DIR / f"{support_id}.png"

        if img_url and not img_path.exists():
            download_image(img_url, img_path)

        cards.append({
            "id": support_id,
            "name": name,
            "image": str(img_path),
            "type": support_type,
            "stats": detail.get("stats", {}),
            "stars": 0,
            "blacklisted": False
        })

        if progress_callback:
            progress_callback("Support Cards", i + 1, total_support)

    # ==========================================================
    # SAVE
    # ==========================================================

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    if status_callback:
        status_callback("Crawl complete.")
