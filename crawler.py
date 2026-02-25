import requests
import os
import json
import logging
import time

DATA_FILE = "data/data.json"
SUPPORT_IMG_DIR = "data/images/support"

CHARA_API = "https://umapyoi.net/api/v1/character"
SUPPORT_API = "https://umapyoi.net/api/v1/support"

# Safe rate limit: 5 requests per second
REQUEST_DELAY = 0.20

os.makedirs("data", exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)


def safe_request(session, url):
    try:
        response = session.get(url, timeout=(5, 15))
        response.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return response.json()
    except Exception as e:
        logging.error(f"Request failed: {url} - {e}")
        return None


def fetch_paginated(session, base_url, status_callback=None):
    results = []
    url = base_url
    page = 1

    while url:
        if status_callback:
            status_callback(f"Fetching page {page}...")

        data = safe_request(session, url)
        if not data:
            break

        results.extend(data.get("results", []))
        url = data.get("next")
        page += 1

    return results


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    if progress_callback:
        progress_callback(1)

    if status_callback:
        status_callback("Connecting to API...")

    session = requests.Session()

    # =============================
    # FETCH HORSES
    # =============================

    horse_data = fetch_paginated(session, CHARA_API, status_callback)

    total_horses = len(horse_data)
    horses = []

    for i, h in enumerate(horse_data, start=1):

        horses.append({
            "id": h["id"],
            "name": h.get("name_en", "Unknown"),
            "preferred_stat": "Speed"
        })

        if progress_callback:
            progress_callback(int((i / total_horses) * 40))

        if status_callback:
            status_callback(f"Horses {i}/{total_horses}")

    # =============================
    # FETCH SUPPORT CARDS
    # =============================

    if status_callback:
        status_callback("Fetching support cards...")

    support_data = fetch_paginated(session, SUPPORT_API, status_callback)

    total_support = len(support_data)
    cards = []

    for i, s in enumerate(support_data, start=1):

        support_id = s["id"]

        img_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{support_id}.png"
        img_path = os.path.join(SUPPORT_IMG_DIR, f"{support_id}.png")

        # Download image only if missing
        if not os.path.exists(img_path):
            try:
                r = session.get(img_url, timeout=(5, 10))
                if r.status_code == 200:
                    with open(img_path, "wb") as f:
                        f.write(r.content)
                time.sleep(REQUEST_DELAY)
            except Exception:
                logging.warning(f"Image failed: {support_id}")

        cards.append({
            "id": support_id,
            "name": s.get("name_en", "Unknown"),
            "rarity": s.get("rarity", "SR"),
            "type": s.get("type", "Speed"),
            "image": img_path,
            "event_bonus": s.get("event_bonus", 0),
            "skills": s.get("skills", []),
            "blacklisted": False
        })

        if progress_callback:
            progress_callback(40 + int((i / total_support) * 60))

        if status_callback:
            status_callback(f"Supports {i}/{total_support}")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Crawl complete")

    logging.info("Crawl complete")
