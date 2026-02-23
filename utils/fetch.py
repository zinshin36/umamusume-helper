import requests
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.storage import (
    ensure_directories,
    load_data,
    save_data,
    deduplicate,
    HORSE_IMG_DIR,
    SUPPORT_IMG_DIR
)


BASE_URL = "https://umamusu.wiki"


def download_image(url, save_path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(save_path, "wb") as f:
                f.write(response.content)
            return True
    except Exception as e:
        logging.error(f"Image download failed: {e}")
    return False


def parse_table(url, save_dir, entry_type, progress_callback):
    logging.info(f"Parsing {entry_type} from {url}")

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table")
    if not table:
        logging.warning(f"No table found at {url}")
        return []

    rows = table.find_all("tr")[1:]  # skip header

    entries = []
    total = len(rows)

    for i, row in enumerate(rows):
        cells = row.find_all("td")
        if not cells:
            continue

        name_cell = cells[0]
        name = name_cell.get_text(strip=True)

        if not name or len(name) < 2:
            continue

        img_tag = name_cell.find("img")
        if not img_tag:
            continue

        img_url = img_tag.get("src")
        if not img_url:
            continue

        img_url = urljoin(BASE_URL, img_url)
        filename = name.replace(" ", "_").replace("/", "_") + ".png"
        save_path = f"{save_dir}/{filename}"

        if download_image(img_url, save_path):
            entries.append({
                "name": name,
                "image": save_path,
                "source": "umamusu_wiki"
            })

        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(percent, f"Processing {entry_type}: {name}")

    return entries


def fetch_all_sites(progress_callback=None):
    ensure_directories()
    logging.info("Starting crawl")

    data = load_data()

    horses_url = f"{BASE_URL}/Game:List_of_Trainees"
    cards_url = f"{BASE_URL}/Game:List_of_Support_Cards"

    horses = parse_table(horses_url, HORSE_IMG_DIR, "Horses", progress_callback)
    cards = parse_table(cards_url, SUPPORT_IMG_DIR, "Support Cards", progress_callback)

    data["horses"] = deduplicate(horses)
    data["cards"] = deduplicate(cards)

    save_data(data)

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    if progress_callback:
        progress_callback(100, "Crawl complete")

    return len(horses), len(cards)
