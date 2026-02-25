import requests
import os
import json
import logging

DATA_FILE = "data/data.json"
HORSE_IMG_DIR = "data/images/horses"
SUPPORT_IMG_DIR = "data/images/support"

UMAPYOI_CHARACTER_API = "https://umapyoi.net/api/v1/character"
UMAPYOI_SUPPORT_API = "https://umapyoi.net/api/v1/support"

os.makedirs(HORSE_IMG_DIR, exist_ok=True)
os.makedirs(SUPPORT_IMG_DIR, exist_ok=True)
os.makedirs("data", exist_ok=True)

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def download_image(url, path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return True
    except Exception:
        return False
    return False


def crawl(progress_callback=None, status_callback=None):

    logging.info("Starting API crawl")

    if status_callback:
        status_callback("Fetching characters...")

    horses = []
    supports = []

    char_response = requests.get(UMAPYOI_CHARACTER_API)
    characters = char_response.json()

    total_steps = len(characters) + 1
    step = 0

    for char in characters:
        step += 1

        if progress_callback:
            progress_callback(int(step / total_steps * 100))

        name = char.get("name_en") or char.get("name")
        char_id = char.get("id")

        if status_callback:
            status_callback(f"Character: {name}")

        horses.append({
            "id": char_id,
            "name": name,
            "preferred_stat": char.get("initial_stat_type", "Speed"),
            "image": f"{HORSE_IMG_DIR}/{char_id}.png"
        })

    # ----------------------------
    # SUPPORT CARDS
    # ----------------------------

    if status_callback:
        status_callback("Fetching support cards...")

    support_response = requests.get(UMAPYOI_SUPPORT_API)
    support_cards = support_response.json()

    total_steps += len(support_cards)

    for card in support_cards:
        step += 1

        if progress_callback:
            progress_callback(int(step / total_steps * 100))

        support_id = card.get("id")
        name = card.get("name_en") or card.get("name")
        rarity = card.get("rarity", "SR")
        card_type = card.get("type", "Speed")

        image_url = f"https://gametora.com/images/umamusume/supports/tex_support_card_{support_id}.png"
        img_path = f"{SUPPORT_IMG_DIR}/{support_id}.png"

        if status_callback:
            status_callback(f"Support: {name}")

        if not os.path.exists(img_path):
            download_image(image_url, img_path)

        supports.append({
            "id": support_id,
            "name": name,
            "rarity": rarity,
            "type": card_type,
            "event_bonus": card.get("event_bonus", 0),
            "skills": card.get("skills", []),
            "image": img_path
        })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": supports}, f, indent=2)

    if progress_callback:
        progress_callback(100)

    if status_callback:
        status_callback("Crawl Complete")

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(supports)}")
