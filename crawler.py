import requests
import json
import logging
import os
from pathlib import Path
from time import sleep

BASE_URL = "https://umapyoi.net"

CHAR_LIST_URL = f"{BASE_URL}/api/v1/character/list"
SUPPORT_IDS_URL = f"{BASE_URL}/api/v1/support"
SUPPORT_DETAIL_URL = f"{BASE_URL}/api/v1/support/{{}}"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json"
}

DATA_DIR = Path("data")
IMG_DIR = DATA_DIR / "images"
HORSE_IMG = IMG_DIR / "horses"
SUPPORT_IMG = IMG_DIR / "support"
DATA_FILE = DATA_DIR / "data.json"

for d in (DATA_DIR, IMG_DIR, HORSE_IMG, SUPPORT_IMG):
    os.makedirs(d, exist_ok=True)


def safe_get_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)

        if r.status_code != 200:
            logging.error(f"HTTP {r.status_code} for {url}")
            logging.error(f"Response text: {r.text[:300]}")
            return None

        if not r.text.strip():
            logging.error(f"Empty response from {url}")
            return None

        return r.json()

    except Exception as e:
        logging.error(f"Request failed {url}: {e}")
        return None


def download_image(url, save_path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
    except Exception as e:
        logging.warning(f"Image download failed: {e}")


def crawl():
    logging.info("Starting API crawl")

    horses = []
    cards = []

    # ------------------------
    # CHARACTERS
    # ------------------------
    char_list = safe_get_json(CHAR_LIST_URL)

    if not char_list:
        logging.error("Character list returned nothing")
    else:
        for c in char_list:
            cid = c.get("id")
            name = c.get("name_en") or c.get("name")

            if not name:
                continue

            img_url = c.get("image_url")
            img_path = HORSE_IMG / f"{cid}.png"

            if img_url and not img_path.exists():
                download_image(img_url, img_path)

            horses.append({
                "id": cid,
                "name": name,
                "image": str(img_path),
                "type": c.get("type", "")
            })

            sleep(0.05)  # 10 req/sec safe

    # ------------------------
    # SUPPORT IDS
    # ------------------------
    support_ids = safe_get_json(SUPPORT_IDS_URL)

    if not support_ids:
        logging.error("Support ID list returned nothing")
    else:
        for sid in support_ids:

            detail = safe_get_json(SUPPORT_DETAIL_URL.format(sid))

            if not detail:
                continue

            cid = detail.get("id")
            name = detail.get("name_en") or detail.get("name")

            if not name:
                continue

            img_url = detail.get("image_url")
            img_path = SUPPORT_IMG / f"{cid}.png"

            if img_url and not img_path.exists():
                download_image(img_url, img_path)

            cards.append({
                "id": cid,
                "name": name,
                "image": str(img_path),
                "stats": detail.get("stats", {}),
                "type": detail.get("type", "")
            })

            sleep(0.05)

    # ------------------------
    # SAVE
    # ------------------------
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")
