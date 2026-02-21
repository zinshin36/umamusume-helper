import os
import requests
import logging

API_URL = "https://umamusume.fandom.com/api.php"

def get_category_members(category_name):
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category_name}",
        "cmlimit": "500",
        "format": "json"
    }
    r = requests.get(API_URL, params=params)
    return r.json().get("query", {}).get("categorymembers", [])


def get_page_image(title):
    params = {
        "action": "query",
        "prop": "pageimages",
        "titles": title,
        "pithumbsize": 400,
        "format": "json"
    }
    r = requests.get(API_URL, params=params)
    pages = r.json().get("query", {}).get("pages", {})
    for page in pages.values():
        if "thumbnail" in page:
            return page["thumbnail"]["source"]
    return None


def download_image(url, path):
    try:
        r = requests.get(url)
        with open(path, "wb") as f:
            f.write(r.content)
    except Exception as e:
        logging.error(str(e))


def fetch_data(progress_callback=None):
    horses = []
    cards = []

    os.makedirs("images/horses", exist_ok=True)
    os.makedirs("images/cards", exist_ok=True)

    try:
        # ----------------------------
        # Horses
        # ----------------------------
        horse_pages = get_category_members("Playable_Uma_Musume")
        total = len(horse_pages)

        for i, page in enumerate(horse_pages):
            name = page["title"]
            image_url = get_page_image(name)

            image_path = None
            if image_url:
                image_path = f"images/horses/{name}.png"
                download_image(image_url, image_path)

            horses.append({
                "name": name,
                "image_path": image_path
            })

            if progress_callback:
                progress_callback(int((i / total) * 50))

        # ----------------------------
        # Support Cards
        # ----------------------------
        card_pages = get_category_members("Support_Cards")
        total_cards = len(card_pages)

        for i, page in enumerate(card_pages):
            name = page["title"]
            image_url = get_page_image(name)

            image_path = None
            if image_url:
                image_path = f"images/cards/{name}.png"
                download_image(image_url, image_path)

            cards.append({
                "name": name,
                "image_path": image_path
            })

            if progress_callback:
                progress_callback(50 + int((i / total_cards) * 50))

    except Exception as e:
        logging.error(str(e))

    if progress_callback:
        progress_callback(100)

    return {"horses": horses, "cards": cards}
