# crawler.py

import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path


HEADERS = {"User-Agent": "Mozilla/5.0"}


def download_image(url, save_dir: Path, name):
    filename = name.replace(" ", "_").replace("/", "_") + ".png"
    path = save_dir / filename

    if path.exists():
        return str(path)

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return str(path)
    except Exception as e:
        logging.error(f"Image download failed: {e}")

    return None


def scrape_list_page(url, progress_callback=None):
    logging.info(f"Scraping {url}")

    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "lxml")

    results = []

    tables = soup.find_all("table")
    total = len(tables)

    for i, table in enumerate(tables):
        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(percent, f"Scanning table {i+1}/{total}")

        for img in table.find_all("img"):
            name = img.get("alt")
            src = img.get("src")

            if not name or not src:
                continue

            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urljoin("https://umamusu.wiki", src)

            results.append((name.strip(), src))

        time.sleep(0.2)

    return results


def crawl_all(base_path: Path, progress_callback=None):

    horse_dir = base_path / "data" / "images" / "horses"
    card_dir = base_path / "data" / "images" / "support"

    horses_raw = scrape_list_page(
        "https://umamusu.wiki/Game:List_of_Trainees",
        progress_callback
    )

    horses = []

    for i, (name, img_url) in enumerate(horses_raw):
        if progress_callback:
            percent = int((i / len(horses_raw)) * 100)
            progress_callback(percent, f"Downloading horse {name}")

        path = download_image(img_url, horse_dir, name)
        if path:
            horses.append({"name": name, "image": path})

        time.sleep(0.1)

    cards_raw = scrape_list_page(
        "https://umamusu.wiki/Game:List_of_Support_Cards",
        progress_callback
    )

    cards = []

    for i, (name, img_url) in enumerate(cards_raw):
        if progress_callback:
            percent = int((i / len(cards_raw)) * 100)
            progress_callback(percent, f"Downloading card {name}")

        path = download_image(img_url, card_dir, name)
        if path:
            cards.append({"name": name, "image": path})

        time.sleep(0.1)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    return {
        "horses": horses,
        "cards": cards,
        "blacklist": []
    }
