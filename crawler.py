import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

BASE = "https://umamusu.wiki"
HEADERS = {"User-Agent": "UmamusumeBuilderBot/1.0"}

HORSE_URL = BASE + "/Game:List_of_Trainees"
SUPPORT_URL = BASE + "/Game:List_of_Support_Cards"


def parse_table_page(url, save_dir: Path, progress_callback, label):
    logging.info(f"Scraping {url}")

    results = []

    response = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(response.text, "lxml")

    tables = soup.find_all("table", class_="wikitable")

    if not tables:
        logging.warning("No wikitable found.")
        return results

    rows = tables[0].find_all("tr")
    total = len(rows)

    for i, row in enumerate(rows[1:], start=1):
        cols = row.find_all("td")
        if not cols:
            continue

        name = cols[0].get_text(strip=True)
        img_tag = cols[0].find("img")

        if not name or not img_tag:
            continue

        img_url = img_tag.get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url
        else:
            img_url = urljoin(BASE, img_url)

        filename = name.replace("/", "_") + ".png"
        save_path = save_dir / filename

        if not save_path.exists():
            try:
                img_data = requests.get(img_url, headers=HEADERS, timeout=10)
                if img_data.status_code == 200:
                    with open(save_path, "wb") as f:
                        f.write(img_data.content)
            except:
                continue

        results.append({
            "name": name,
            "image": str(save_path)
        })

        percent = int((i / total) * 100)
        progress_callback(percent, f"{label}: {percent}%")

        time.sleep(0.5)  # respectful delay

    return results


def crawl_all(base_dir: Path, progress_callback):
    horse_dir = base_dir / "data" / "images" / "horses"
    support_dir = base_dir / "data" / "images" / "support"

    horses = parse_table_page(HORSE_URL, horse_dir, progress_callback, "Horses")
    cards = parse_table_page(SUPPORT_URL, support_dir, progress_callback, "Support")

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    return {
        "horses": horses,
        "cards": cards
    }
