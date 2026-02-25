import requests
import os
import json
import logging
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

DATA_FILE = "data/data.json"
SUPPORT_IMG_DIR = "data/images/support"

CHARA_API = "https://umapyoi.net/api/v1/character"
SUPPORT_API = "https://umapyoi.net/api/v1/support"

os.makedirs("data", exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)


def create_session():
    session = requests.Session()

    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )

    adapter = HTTPAdapter(max_retries=retries)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    return session


def safe_get_json(session, url):
    try:
        response = session.get(url, timeout=(5, 15))  # 5 sec connect, 15 sec read
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Request failed for {url}: {e}")
        return None


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    if progress_callback:
        progress_callback(1)

    if status_callback:
        status_callback("Connecting to API...")

    session = create_session()

    # ---------------- HORSES ----------------

    horse_data = safe_get_json(session, CHARA_API)

    if horse_data is None:
        if status_callback:
            status_callback("Horse API failed.")
        return

    horses = []
    total_horses = len(horse_data)

    for i, h in enumerate(horse_data, start=1):

        horses.append({
            "id": h["id"],
            "name": h.get("name_en", "Unknown"),
            "preferred_stat": "Speed"
        })

        if status_callback:
            status_callback(f"Horses {i}/{total_horses}")

        if progress_callback:
            progress_callback(int((i / total_horses) * 40))

    # ---------------- SUPPORTS ----------------

    if status_callback:
        status_callback("Fetching support cards...")

    support_data = safe_get_json(session, SUPPORT_API)

    if support_data is None:
        if status_callback:
            status_callback("Support API failed.")
        return

    cards = []
    total_support = len(support_data)

    for i, s in enumerate(support_data, start=1):

        support_id = s["id"]

        img_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{support_id}.png"
        img_path = os.path.join(SUPPORT_IMG_DIR, f"{support_id}.png")

        try:
            r = session.get(img_url, timeout=(5, 10))
            if r.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(r.content)
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

        if status_callback:
            status_callback(f"Supports {i}/{total_support}")

        if progress_callback:
            progress_callback(40 + int((i / total_support) * 60))

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Crawl complete")

    logging.info("Crawl complete")
