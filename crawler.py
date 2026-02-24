import requests
import json
import os
import logging
from pathlib import Path
from time import sleep

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


def safe_json(url):
    r = requests.get(url, headers=HEADERS)
    if r.status_code != 200:
        logging.error(f"HTTP {r.status_code} for {url}")
        return None
    try:
        return r.json()
    except:
        logging.error(f"Bad JSON from {url}")
        return None


def download_image(url, path):
    try:
        r = requests.get(url, headers=HEADERS)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
    except:
        pass


def crawl(progress_callback=None):

    horses = []
    cards = []

    logging.info("Starting API crawl")

    # -------- CHARACTERS --------
    char_list = safe_json(f"{BASE}/character")
    if char_list:
        for i, c in enumerate(char_list):
            cid = c["id"]
            name = c.get("name_en") or c.get("name")
            img_url = c.get("image_url")

            img_path = HORSE_DIR / f"{cid}.png"
            if img_url and not img_path.exists():
                download_image(img_url, img_path)

            horses.append({
                "id": cid,
                "name": name,
                "image": str(img_path)
            })

            if progress_callback:
                progress_callback("Characters", i+1, len(char_list))

            sleep(0.1)

    # -------- SUPPORT LIST --------
    support_list = safe_json(f"{BASE}/support")
    if support_list:
        total = len(support_list)

        for i, s in enumerate(support_list):

            sid = s["id"]   # FIX: use ID only

            detail = safe_json(f"{BASE}/support/{sid}")
            if not detail:
                continue

            name = detail.get("name_en") or detail.get("name")
            img_url = detail.get("image_url")

            img_path = SUPPORT_DIR / f"{sid}.png"
            if img_url and not img_path.exists():
                download_image(img_url, img_path)

            cards.append({
                "id": sid,
                "name": name,
                "image": str(img_path),
                "type": detail.get("type"),
                "stats": detail.get("stats", {}),
                "stars": 0,
                "blacklisted": False
            })

            if progress_callback:
                progress_callback("Support Cards", i+1, total)

            sleep(0.1)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")
