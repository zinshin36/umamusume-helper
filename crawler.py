import requests
import time
import logging
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from data_manager import load_data, save_data, HORSE_IMG_DIR, SUPPORT_IMG_DIR

BASE = "https://umamusu.wiki"
HEADERS = {"User-Agent": "Mozilla/5.0"}


def download_image(url, folder, name):
    filename = name.replace(" ", "_").replace("/", "_") + ".png"
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        return path

    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return path
    except Exception as e:
        logging.error(f"Image download failed: {e}")

    return None


def scrape_page(url, entry_type, progress_callback=None):
    logging.info(f"Scraping {url}")

    r = requests.get(url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "lxml")

    results = []

    tables = soup.find_all("table")
    total_tables = len(tables)

    for i, table in enumerate(tables):

        if progress_callback:
            percent = int((i / total_tables) * 100)
            progress_callback(percent, f"Scanning {entry_type} table {i+1}/{total_tables}")

        rows = table.find_all("tr")

        for row in rows:
            img = row.find("img")
            if not img:
                continue

            name = img.get("alt")
            src = img.get("src")

            if not name or not src:
                continue

            if src.startswith("//"):
                src = "https:" + src
            elif src.startswith("/"):
                src = urljoin(BASE, src)

            results.append({
                "name": name.strip(),
                "image_url": src
            })

        time.sleep(0.2)  # slow down to avoid blocking

    return results


def crawl_all(progress_callback=None):
    data = load_data()

    if progress_callback:
        progress_callback(0, "Scraping horses...")

    horses_raw = scrape_page(
        "https://umamusu.wiki/Game:List_of_Trainees",
        "horses",
        progress_callback
    )

    horses = []
    for i, entry in enumerate(horses_raw):
        if progress_callback:
            percent = int((i / len(horses_raw)) * 100)
            progress_callback(percent, f"Downloading horse {entry['name']}")

        path = download_image(entry["image_url"], HORSE_IMG_DIR, entry["name"])
        if path:
            horses.append({
                "name": entry["name"],
                "image": path,
                "stars": 0
            })

        time.sleep(0.1)

    if progress_callback:
        progress_callback(0, "Scraping support cards...")

    cards_raw = scrape_page(
        "https://umamusu.wiki/Game:List_of_Support_Cards",
        "support",
        progress_callback
    )

    cards = []
    for i, entry in enumerate(cards_raw):
        if progress_callback:
            percent = int((i / len(cards_raw)) * 100)
            progress_callback(percent, f"Downloading card {entry['name']}")

        path = download_image(entry["image_url"], SUPPORT_IMG_DIR, entry["name"])
        if path:
            cards.append({
                "name": entry["name"],
                "image": path,
                "stars": 0
            })

        time.sleep(0.1)

    data["horses"] = horses
    data["cards"] = cards

    save_data(data)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    if progress_callback:
        progress_callback(100, "Finished")

    return len(horses), len(cards)
