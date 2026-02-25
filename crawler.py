import requests
import os
import json
import logging

DATA_FILE = "data/data.json"
HORSE_IMG_DIR = "data/images/horses"
SUPPORT_IMG_DIR = "data/images/support"

CHARA_API = "https://umapyoi.net/api/v1/character"
SUPPORT_API = "https://umapyoi.net/api/v1/support"

os.makedirs(HORSE_IMG_DIR, exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    horses = []
    cards = []

    # ---------------- HORSES ----------------

    horse_res = requests.get(CHARA_API)
    horse_data = horse_res.json()

    total_horses = len(horse_data)

    for index, h in enumerate(horse_data, start=1):

        horse_id = h["id"]
        name = h["name_en"]

        horses.append({
            "id": horse_id,
            "name": name,
            "preferred_stat": "Speed"
        })

        if status_callback:
            status_callback(f"Fetching horses {index}/{total_horses}")

        if progress_callback:
            percent = int((index / total_horses) * 40)
            progress_callback(percent)

    # ---------------- SUPPORTS ----------------

    support_res = requests.get(SUPPORT_API)
    support_data = support_res.json()

    total_support = len(support_data)

    for index, s in enumerate(support_data, start=1):

        support_id = s["id"]
        name = s["name_en"]
        rarity = s.get("rarity", "SR")
        card_type = s.get("type", "Speed")

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
            "name": name,
            "rarity": rarity,
            "type": card_type,
            "image": img_path,
            "event_bonus": s.get("event_bonus", 0),
            "skills": s.get("skills", []),
            "blacklisted": False
        })

        if status_callback:
            status_callback(f"Downloading supports {index}/{total_support}")

        if progress_callback:
            percent = 40 + int((index / total_support) * 60)
            progress_callback(percent)

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Crawl complete")

    logging.info("Crawl complete")
