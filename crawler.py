import requests
import os
import json
import logging
import time

DATA_FILE = "data/data.json"
SUPPORT_IMG_DIR = "data/images/support"

CHARA_API = "https://umapyoi.net/api/v1/character/list"
SUPPORT_API = "https://umapyoi.net/api/v1/support"

REQUEST_DELAY = 0.15  # ~6.6 requests/sec (safe under 10/sec limit)

os.makedirs("data", exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "UmaPlannerPRO/1.0"
    })

    if progress_callback:
        progress_callback(1)

    if status_callback:
        status_callback("Fetching horse list...")

    # ========================
    # FETCH HORSES
    # ========================

    try:
        r = session.get(CHARA_API, timeout=(5, 15))
        r.raise_for_status()
        horse_data = r.json()
        time.sleep(REQUEST_DELAY)
    except Exception as e:
        logging.error(f"Horse API failed: {e}")
        if status_callback:
            status_callback("Horse API failed")
        return

    horses = []
    total_horses = len(horse_data)

    if status_callback:
        status_callback(f"Loaded {total_horses} horses")

    for i, h in enumerate(horse_data, start=1):

        horses.append({
            "id": h["id"],
            "name": h.get("name_en", "Unknown"),
            "preferred_stat": "Speed"
        })

        if progress_callback:
            progress_callback(int((i / total_horses) * 40))

    # ========================
    # FETCH SUPPORT CARDS
    # ========================

    if status_callback:
        status_callback("Fetching support card list...")

    try:
        r = session.get(SUPPORT_API, timeout=(5, 15))
        r.raise_for_status()
        support_data = r.json()
        time.sleep(REQUEST_DELAY)
    except Exception as e:
        logging.error(f"Support API failed: {e}")
        if status_callback:
            status_callback("Support API failed")
        return

    cards = []
    total_support = len(support_data)

    if status_callback:
        status_callback(f"Loaded {total_support} support cards")

    for i, s in enumerate(support_data, start=1):

        support_id = s["id"]

        img_path = os.path.join(SUPPORT_IMG_DIR, f"{support_id}.png")

        # Only download image if missing
        if not os.path.exists(img_path):

            img_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{support_id}.png"

            try:
                img_res = session.get(img_url, timeout=(5, 10))
                if img_res.status_code == 200:
                    with open(img_path, "wb") as f:
                        f.write(img_res.content)
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
        json.dump({
            "horses": horses,
            "cards": cards
        }, f, indent=2)

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Crawl complete")

    logging.info("Crawl complete")
