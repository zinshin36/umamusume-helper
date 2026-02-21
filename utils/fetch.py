import os
import requests
import time
from utils.merge import slugify

API_URL = "https://umamusume.fandom.com/api.php"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_category(category):
    members = []
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category}",
        "cmlimit": 500,
        "format": "json"
    }

    r = requests.get(API_URL, params=params, headers=HEADERS)
    data = r.json()

    if "query" in data:
        members = data["query"]["categorymembers"]

    return members

def get_image(title):
    params = {
        "action": "query",
        "prop": "pageimages",
        "titles": title,
        "pithumbsize": 400,
        "format": "json"
    }

    r = requests.get(API_URL, params=params, headers=HEADERS)
    pages = r.json().get("query", {}).get("pages", {})

    for page in pages.values():
        if "thumbnail" in page:
            return page["thumbnail"]["source"]

    return None

def download_image(url, path):
    try:
        r = requests.get(url, headers=HEADERS)
        with open(path, "wb") as f:
            f.write(r.content)
    except:
        pass

def fetch_all(progress_callback=None):
    characters = []
    supports = []

    os.makedirs("images/characters", exist_ok=True)
    os.makedirs("images/support_cards", exist_ok=True)

    # ---------- CHARACTERS ----------
    char_pages = get_category("Playable_Uma_Musume")
    total = len(char_pages)

    for i, page in enumerate(char_pages):
        name = page["title"]
        char_id = slugify(name)

        img_url = get_image(name)
        image_path = None

        if img_url:
            image_path = f"images/characters/{char_id}.png"
            if not os.path.exists(image_path):
                download_image(img_url, image_path)

        characters.append({
            "id": char_id,
            "name": name,
            "versions": [],
            "images": [image_path] if image_path else [],
            "sources": ["Fandom"]
        })

        if progress_callback:
            progress_callback(int((i / max(total,1)) * 50))

        time.sleep(0.2)

    # ---------- SUPPORT CARDS ----------
    support_pages = get_category("Support_Cards")
    total2 = len(support_pages)

    for i, page in enumerate(support_pages):
        name = page["title"]
        card_id = slugify(name)

        img_url = get_image(name)
        image_path = None

        if img_url:
            image_path = f"images/support_cards/{card_id}.png"
            if not os.path.exists(image_path):
                download_image(img_url, image_path)

        supports.append({
            "id": card_id,
            "name": name,
            "rarity": "Unknown",
            "type": "Unknown",
            "bonuses": {},
            "skills": [],
            "images": [image_path] if image_path else [],
            "sources": ["Fandom"]
        })

        if progress_callback:
            progress_callback(50 + int((i / max(total2,1)) * 50))

        time.sleep(0.2)

    if progress_callback:
        progress_callback(100)

    return characters, supports
