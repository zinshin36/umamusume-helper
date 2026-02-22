import requests
import logging
import time
from bs4 import BeautifulSoup
from config import HORSES_PAGE, CARDS_PAGE

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_page(url):
    logging.info(f"Fetching page: {url}")
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()
    return response.text


def parse_category_page(html):
    soup = BeautifulSoup(html, "lxml")

    results = []

    gallery_items = soup.select(".gallerybox")

    for item in gallery_items:
        name_tag = item.select_one(".gallerytext a")
        img_tag = item.select_one("img")

        if not name_tag:
            continue

        name = name_tag.get_text(strip=True)

        image_url = None
        if img_tag and img_tag.get("src"):
            image_url = img_tag["src"]
            if image_url.startswith("//"):
                image_url = "https:" + image_url

        results.append({
            "name": name,
            "image": image_url
        })

    return results


def fetch_all_data():
    start = time.time()
    logging.info("Starting full data fetch...")

    try:
        horses_html = fetch_page(HORSES_PAGE)
        cards_html = fetch_page(CARDS_PAGE)

        horses = parse_category_page(horses_html)
        cards = parse_category_page(cards_html)

        logging.info(f"Horses fetched: {len(horses)}")
        logging.info(f"Cards fetched: {len(cards)}")

        logging.info(f"Fetch duration: {round(time.time() - start, 2)}s")

        return horses, cards

    except Exception as e:
        logging.exception("Error during fetch_all_data")
        raise e
