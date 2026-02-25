import requests
import os
import json
import logging
import time

DATA_FILE = "data/data.json"
SUPPORT_IMG_DIR = "data/images/support"

CHARA_LIST_API = "https://umapyoi.net/api/v1/character/list"
CHARA_DETAIL_API = "https://umapyoi.net/api/v1/character/{}"

SUPPORT_LIST_API = "https://umapyoi.net/api/v1/support"
SUPPORT_DETAIL_API = "https://umapyoi.net/api/v1/support/{}"

REQUEST_DELAY = 0.20  # 5 requests/sec (safe)

os.makedirs("data", exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)


def safe_get(session, url):
    try:
        r = session.get(url, timeout=(5, 15))
        r.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return r.json()
    except Exception as e:
        logging.error(f"Request failed {url}: {e}")
        return None


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    session = requests.Session()
    session.headers.update({"User-Agent": "UmaPlannerPRO/2.0"})

    # ==========================
    # HORSES
    # ==========================

    if status_callback:
        status_callback("Fetching horse list...")

    horse_list = safe_get(session, CHARA_LIST_API)
    if not horse_list:
        return

    horses = []
    total_horses = len(horse_list)

    for i, h in enumerate(horse_list, start=1):

        detail = safe_get(session, CHARA_DETAIL_API.format(h["id"]))
        if not detail:
            continue

        horses.append({
            "id": detail["id"],
            "name": detail.get("name_en", detail.get("name", "Unknown")),
            "speed_growth": detail.get("speed_growth", 0),
            "stamina_growth": detail.get("stamina_growth", 0),
            "power_growth": detail.get("power_growth", 0),
            "guts_growth": detail.get("guts_growth", 0),
            "wisdom_growth": detail.get("wisdom_growth", 0)
        })

        if progress_callback:
            progress_callback(int((i / total_horses) * 40))

        if status_callback:
            status_callback(f"Horses {i}/{total_horses}")

    # ==========================
    # SUPPORT CARDS
    # ==========================

    if status_callback:
        status_callback("Fetching support list...")

    support_ids = safe_get(session, SUPPORT_LIST_API)
    if not support_ids:
        return

    cards = []
    total_support = len(support_ids)

    for i, s in enumerate(support_ids, start=1):

        detail = safe_get(session, SUPPORT_DETAIL_API.format(s["id"]))
        if not detail:
            continue

        support_id = detail["id"]

        img_path = os.path.join(SUPPORT_IMG_DIR, f"{support_id}.png")

        if not os.path.exists(img_path):
            img_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{support_id}.png"
            try:
                img_res = session.get(img_url, timeout=(5, 10))
                if img_res.status_code == 200:
                    with open(img_path, "wb") as f:
                        f.write(img_res.content)
                time.sleep(REQUEST_DELAY)
            except Exception:
                pass

        cards.append({
            "id": support_id,
            "name": detail.get("name_en", detail.get("name", "Unknown")),
            "rarity": detail.get("rarity", "R"),
            "type": detail.get("type", "Speed"),
            "event_bonus": detail.get("event_bonus", 0),
            "training_bonus": detail.get("training_bonus", 0),
            "initial_bond": detail.get("initial_bond", 0),
            "skills": [skill.get("name_en", "") for skill in detail.get("skills", [])],
            "image": img_path,
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
