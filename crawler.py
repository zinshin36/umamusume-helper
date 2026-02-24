import requests
import json
import logging
import os
from pathlib import Path
from time import sleep

# API endpoints
CHAR_LIST_URL = "https://umapyoi.net/api/v1/character/list"
SUPPORT_IDS_URL = "https://umapyoi.net/api/v1/support"
SUPPORT_DETAIL_URL = "https://umapyoi.net/api/v1/support/{}"

# output
DATA_DIR = Path("data")
IMG_DIR = DATA_DIR / "images"
HORSE_IMG = IMG_DIR / "horses"
SUPPORT_IMG = IMG_DIR / "support"
DATA_FILE = DATA_DIR / "data.json"

# ensure dirs
for d in (DATA_DIR, IMG_DIR, HORSE_IMG, SUPPORT_IMG):
    os.makedirs(d, exist_ok=True)


def download_image(url, save_path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        logging.warning(f"Image download failed {url}: {e}")
    return False


def crawl():
    logging.info("Starting API crawl")

    # fetch characters list
    char_list_resp = requests.get(CHAR_LIST_URL).json()
    horses = []

    for c in char_list_resp:
        cid = c.get("id")
        name = c.get("name_en") or c.get("name")
        if not name:
            continue

        img = c.get("image_url")
        img_file = HORSE_IMG / f"{cid}.png"
        if img and not img_file.exists():
            download_image(img, img_file)

        horses.append({
            "id": cid,
            "name": name,
            "image": str(img_file),
            "type": c.get("type", "")
        })

        sleep(0.1)  # rate limit

    # fetch support card full data
    support_ids = requests.get(SUPPORT_IDS_URL).json()
    cards = []

    for sid in support_ids:
        # detail
        detail = requests.get(SUPPORT_DETAIL_URL.format(sid)).json()

        cid = detail.get("id")
        name = detail.get("name_en") or detail.get("name")

        if not name:
            continue

        img = detail.get("image_url")
        img_file = SUPPORT_IMG / f"{cid}.png"
        if img and not img_file.exists():
            download_image(img, img_file)

        cards.append({
            "id": cid,
            "name": name,
            "image": str(img_file),
            "stats": detail.get("stats", {}),
            "type": detail.get("type", "")
        })

        sleep(0.1)  # rate limit

    # save JSON
    all_data = {"horses": horses, "cards": cards}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_data, f, indent=2)

    logging.info(f"Crawl finished. Horses: {len(horses)} Cards: {len(cards)}")
