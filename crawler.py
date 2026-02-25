import requests
import os
import json
import logging

DATA_FILE = "data/data.json"
SUPPORT_IMG_DIR = "data/images/support"

CHARA_API = "https://umapyoi.net/api/v1/character"
SUPPORT_API = "https://umapyoi.net/api/v1/support"

os.makedirs("data", exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    horses = []
    cards = []

    try:
        horse_res = requests.get(CHARA_API, timeout=15)
        horse_data = horse_res.json()
    except Exception as e:
        logging.error(f"Horse API failed: {e}")
        return

    total_horses = len(horse_data)

    for i, h in enumerate(horse_data, start=1):

        horses.append({
            "id": h["id"],
            "name": h["name_en"],
            "preferred_stat": "Speed"
        })

        if status_callback:
            status_callback(f"Horses {i}/{total_horses}")

        if progress_callback:
            progress_callback(int((i / total_horses) * 30))

    try:
        support_res = requests.get(SUPPORT_API, timeout=15)
        support_data = support_res.json()
    except Exception as e:
        logging.error(f"Support API failed: {e}")
        return

    total_support = len(support_data)

    for i, s in enumerate(support_data, start=1):

        support_id = s["id"]

        img_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{support_id}.png"
        img_path = os.path.join(SUPPORT_IMG_DIR, f"{support_id}.png")

        try:
            r = requests.get(img_url, timeout=10)
            if r.status_code == 200:
                with open(img_path, "wb") as f:
                    f.write(r.content)
        except:
            logging.warning(f"Image failed: {support_id}")

        cards.append({
            "id": support_id,
            "name": s["name_en"],
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
            progress_callback(30 + int((i / total_support) * 70))

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Crawl complete")

    logging.info("Crawl complete")
