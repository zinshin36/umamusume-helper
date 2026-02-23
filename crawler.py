import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

BASE = "https://umamusu.wiki"
HEADERS = {
    "User-Agent": "UmamusumeBuilderBot/1.0 (+respectful crawler)"
}

HORSE_LIST = BASE + "/Game:List_of_Trainees"
SUPPORT_LIST = BASE + "/Game:List_of_Support_Cards"


def get_character_links(list_url):
    logging.info(f"Fetching list page: {list_url}")

    r = requests.get(list_url, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(r.text, "lxml")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # only keep actual character pages
        if href.startswith("/wiki/") and ":" not in href:
            full = urljoin(BASE, href)
            links.append(full)

    # remove duplicates
    links = list(set(links))
    logging.info(f"Found {len(links)} links")

    return links


def scrape_profile(url, save_dir: Path):
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        soup = BeautifulSoup(r.text, "lxml")

        title = soup.find("h1")
        if not title:
            return None

        name = title.get_text(strip=True)

        infobox = soup.find("table", class_="infobox")
        if not infobox:
            return None

        img = infobox.find("img")
        if not img:
            return None

        img_url = img.get("src")
        if img_url.startswith("//"):
            img_url = "https:" + img_url

        filename = name.replace("/", "_") + ".png"
        path = save_dir / filename

        if not path.exists():
            img_data = requests.get(img_url, headers=HEADERS, timeout=20)
            if img_data.status_code == 200:
                with open(path, "wb") as f:
                    f.write(img_data.content)

        return {
            "name": name,
            "image": str(path)
        }

    except Exception as e:
        logging.warning(f"Failed to scrape {url}: {e}")
        return None


def crawl_section(list_url, save_dir: Path, progress_callback, label):

    links = get_character_links(list_url)
    results = []

    total = len(links)

    for i, link in enumerate(links, start=1):
        result = scrape_profile(link, save_dir)
        if result:
            results.append(result)

        percent = int((i / total) * 100)
        progress_callback(percent, f"{label}: {percent}%")

        time.sleep(1)  # respect robots

    return results


def crawl_all(base_dir: Path, progress_callback):

    horse_dir = base_dir / "data" / "images" / "horses"
    support_dir = base_dir / "data" / "images" / "support"

    logging.info("Starting crawl")

    horses = crawl_section(HORSE_LIST, horse_dir, progress_callback, "Horses")
    cards = crawl_section(SUPPORT_LIST, support_dir, progress_callback, "Support")

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    return {
        "horses": horses,
        "cards": cards
    }
