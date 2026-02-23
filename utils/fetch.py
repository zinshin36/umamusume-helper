import requests
import logging
import os
from urllib.parse import quote
from utils.storage import (
    ensure_directories,
    load_data,
    save_data,
    HORSE_IMG_DIR,
    SUPPORT_IMG_DIR
)

API_URL = "https://umamusu.wiki/api.php"


def get_page_images(page_title):
    params = {
        "action": "query",
        "prop": "images",
        "titles": page_title,
        "format": "json",
        "imlimit": "max"
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    pages = data["query"]["pages"]
    images = []

    for page_id in pages:
        if "images" in pages[page_id]:
            for img in pages[page_id]["images"]:
                images.append(img["title"])

    return images


def get_image_url(image_title):
    params = {
        "action": "query",
        "titles": image_title,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }

    response = requests.get(API_URL, params=params)
    data = response.json()

    pages = data["query"]["pages"]
    for page_id in pages:
        if "imageinfo" in pages[page_id]:
            return pages[page_id]["imageinfo"][0]["url"]

    return None


def download_image(url, save_dir):
    filename = os.path.basename(url)
    save_path = os.path.join(save_dir, filename)

    if os.path.exists(save_path):
        return save_path

    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path

    return None


def fetch_page(page_title, save_dir, progress_callback):
    logging.info(f"Fetching {page_title}")

    image_titles = get_page_images(page_title)
    entries = []

    total = len(image_titles)

    for index, image_title in enumerate(image_titles):
        if not image_title.lower().endswith((".png", ".jpg", ".jpeg")):
            continue

        name = image_title.replace("File:", "").rsplit(".", 1)[0]

        img_url = get_image_url(image_title)
        if not img_url:
            continue

        path = download_image(img_url, save_dir)
        if not path:
            continue

        entries.append({
            "name": name,
            "image": path,
            "source": "umamusu_wiki"
        })

        if progress_callback:
            percent = int((index / total) * 100)
            progress_callback(percent, f"Downloading {name}")

    return entries


def fetch_all_sites(progress_callback=None):
    ensure_directories()
    logging.info("Starting crawl via MediaWiki API")

    data = load_data()

    horses = fetch_page("Game:List_of_Trainees", HORSE_IMG_DIR, progress_callback)
    cards = fetch_page("Game:List_of_Support_Cards", SUPPORT_IMG_DIR, progress_callback)

    data["horses"] = horses
    data["cards"] = cards

    save_data(data)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    if progress_callback:
        progress_callback(100, "Crawl complete")

    return len(horses), len(cards)
