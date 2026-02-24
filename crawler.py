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

HEADERS = {"User-Agent": "Mozilla/5.0"}
TIMEOUT = 20


def get_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200:
            return r.json()
        logging.error(f"HTTP {r.status_code} for {url}")
    except Exception as e:
        logging.error(f"JSON failure: {url} | {e}")
    return None


def download(url, path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
        if r.status_code == 200 and r.content:
            with open(path, "wb") as f:
                f.write(r.content)
        else:
            logging.error(f"Image failed: {url}")
    except Exception as e:
        logging.error(f"Image error: {url} | {e}")


def crawl(progress=None, status=None):

    logging.info("Starting API crawl")
    if status:
        status("Starting crawl...")

    horses = []
    cards = []

    char_list = get_json(f"{BASE}/character/list")
    if not char_list:
        logging.error("Character list failed.")
        return

    total_chars = len(char_list)
    total_support = 0

    for i, c in enumerate(char_list):
        cid = c["id"]
        name = c.get("name_en") or c.get("name")

        img_api = get_json(f"{BASE}/character/images/{cid}")
        img_url = None

        if isinstance(img_api, list) and img_api:
            img_url = img_api[0].get("url")

        img_path = HORSE_DIR / f"{cid}.png"
        if img_url:
            download(img_url, img_path)

        horses.append({
            "id": cid,
            "name": name,
            "image": str(img_path)
        })

        percent = int(((i + 1) / total_chars) * 50)
        if progress:
            progress(percent)
        if status:
            status(f"Crawling horses {i+1}/{total_chars}")

    support_list = get_json(f"{BASE}/support")
    total_support = len(support_list)

    for i, s in enumerate(support_list):
        sid = s["id"]

        detail = get_json(f"{BASE}/support/{sid}")
        name = detail.get("name_en") if detail else None
        support_type = detail.get("type") if detail else None

        img_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{sid}.png"
        img_path = SUPPORT_DIR / f"{sid}.png"
        download(img_url, img_path)

        cards.append({
            "id": sid,
            "name": name,
            "type": support_type,
            "image": str(img_path),
            "stars": 0,
            "blacklisted": False
        })

        percent = 50 + int(((i + 1) / total_support) * 50)
        if progress:
            progress(percent)
        if status:
            status(f"Crawling supports {i+1}/{total_support}")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")
    if status:
        status("Crawl complete")
