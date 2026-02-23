import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import logging

BASE_URL = "https://umamusu.wiki"
HEADERS = {"User-Agent": "Mozilla/5.0"}

HORSE_URL = "https://umamusu.wiki/Game:List_of_Trainees"
SUPPORT_URL = "https://umamusu.wiki/Game:List_of_Support_Cards"


def ensure_image_dirs():
    os.makedirs("data/images/horses", exist_ok=True)
    os.makedirs("data/images/support", exist_ok=True)


def download_image(img_url, save_path):
    try:
        r = requests.get(img_url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(r.content)
            return True
    except Exception as e:
        logging.warning(f"Image download failed: {e}")
    return False


def parse_gallery_page(url, image_folder):
    logging.info(f"Scraping {url}")
    results = []

    response = requests.get(url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Wiki uses gallerybox class
    gallery_items = soup.find_all("div", class_="gallerybox")

    if not gallery_items:
        logging.warning("No gallery items found.")
        return results

    for item in gallery_items:
        try:
            link = item.find("a")
            img = item.find("img")

            if not link or not img:
                continue

            name = link.get("title")
            img_url = img.get("src")

            if not img_url:
                continue

            img_url = urljoin(BASE_URL, img_url)

            filename = f"{name.replace('/', '_')}.png"
            save_path = os.path.join(image_folder, filename)

            download_image(img_url, save_path)

            results.append({
                "name": name,
                "image": save_path
            })

        except Exception as e:
            logging.warning(f"Parse error: {e}")

    return results


def fetch_all_sites():
    ensure_image_dirs()

    horses = parse_gallery_page(HORSE_URL, "data/images/horses")
    cards = parse_gallery_page(SUPPORT_URL, "data/images/support")

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    return {
        "horses": horses,
        "cards": cards
    }
