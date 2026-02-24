import requests
import os
import json
import logging
from bs4 import BeautifulSoup
from time import sleep

DATA_DIR = "data"
IMG_DIR = os.path.join(DATA_DIR, "images")
HORSE_IMG_DIR = os.path.join(IMG_DIR, "horses")
CARD_IMG_DIR = os.path.join(IMG_DIR, "support")

DATA_FILE = os.path.join(DATA_DIR, "data.json")

API_CHAR = "https://umapyoi.net/api/v1/character"
API_SUPPORT = "https://umapyoi.net/api/v1/support"

GAMETORA_CHAR = "https://gametora.com/umamusume/characters"
GAMETORA_SUPPORT = "https://gametora.com/umamusume/supports"


def ensure_dirs():
    os.makedirs(HORSE_IMG_DIR, exist_ok=True)
    os.makedirs(CARD_IMG_DIR, exist_ok=True)


def get_gametora_names(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    names = set()

    for a in soup.find_all("a"):
        text = a.get_text(strip=True)
        if len(text) > 3:
            names.add(text.lower())

    return names


def download_image(url, path):
    if not url:
        return None
    if os.path.exists(path):
        return path

    r = requests.get(url)
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        sleep(0.1)
        return path
    return None


def crawl():
    logging.info("Starting API crawl")
    ensure_dirs()

    global_chars = get_gametora_names(GAMETORA_CHAR)
    global_support = get_gametora_names(GAMETORA_SUPPORT)

    horses = []
    cards = []

    char_data = requests.get(API_CHAR).json()
    support_data = requests.get(API_SUPPORT).json()

    for c in char_data:
        name = c.get("name_en", "")
        if name.lower() not in global_chars:
            continue

        img_url = c.get("image_url")
        img_path = os.path.join(HORSE_IMG_DIR, f"{c['id']}.png")
        download_image(img_url, img_path)

        horses.append({
            "id": c["id"],
            "name": name,
            "type": c.get("type", "speed"),
            "rarity": c.get("rarity", 1),
            "image": img_path
        })

    for s in support_data:
        name = s.get("name_en", "")
        if name.lower() not in global_support:
            continue

        img_url = s.get("image_url")
        img_path = os.path.join(CARD_IMG_DIR, f"{s['id']}.png")
        download_image(img_url, img_path)

        cards.append({
            "id": s["id"],
            "name": name,
            "type": s.get("type", "speed"),
            "rarity": s.get("rarity", 1),
            "stats": s.get("stats", {}),
            "image": img_path
        })

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({"horses": horses, "cards": cards}, f, indent=2)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")
