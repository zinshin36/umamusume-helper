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

TIMEOUT = 10


def safe_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code != 200:
            logging.error(f"HTTP {r.status_code} for {url}")
            return None
        return r.json()
    except Exception as e:
        logging.error(f"Request failed: {url} | {e}")
        return None


def download_image(url, path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
    except:
        pass


def crawl(progress_callback=None, status_callback=None):

    horses = []
    cards = []

    logging.info("Starting API crawl")

    # ---------------- CHARACTERS ----------------

    if status_callback:
        status_callback("Fetching character list...")

    char_list = safe_json(f"{BASE}/character")

    if not char_list:
        logging.error("Character list failed.")
        return

    total_chars = len(char_list)

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
            progress_callback("Characters", i + 1, total_chars)

    # ---------------- SUPPORT LIST ----------------

    if status_callback:
        status_callback("Fetching support list...")

    support_list = safe_json(f"{BASE}/support")

    if not support_list:
        logging.error("Support list failed.")
        return

    total_support = len(support_list)

    for i, s in enumerate(support_list):

        sid = s["id"]

        if status_callback:
            status_callback(f"Fetching support {i+1}/{total_support}")

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
            progress_callback("Support Cards", i + 1, total_support)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    if status_callback:
        status_callback("Crawl complete.")
