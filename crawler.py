import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path

BASE = "https://umamusu.wiki"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive"
}

session = requests.Session()
session.headers.update(HEADERS)

HORSE_LIST = BASE + "/Game:List_of_Trainees"
SUPPORT_LIST = BASE + "/Game:List_of_Support_Cards"


def get_character_links(list_url):
    logging.info(f"Fetching list page: {list_url}")

    r = session.get(list_url, timeout=30, allow_redirects=True)

    if r.status_code != 200:
        logging.warning(f"Failed request: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "lxml")

    links = []

    for a in soup.select("a[href^='/wiki/']"):
        href = a["href"]

        if ":" in href:
            continue

        full = urljoin(BASE, href)
        links.append(full)

    links = list(set(links))

    logging.info(f"Found {len(links)} links")
    return links


def scrape_profile(url, save_dir: Path):
    try:
        r = session.get(url, timeout=30)
        if r.status_code != 200:
            return None

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
            img_data = session.get(img_url, timeout=30)
            if img_data.status_code == 200:
                with open(path, "wb") as f:
                    f.write(img_data.content)

        return {
            "name": name,
            "image": str(path)
        }

    except Exception as e:
        logging.warning(f"Failed scraping {url}: {e}")
        return None


def crawl_section(list_url, save_dir: Path, progress_callback, label):

    links = get_character_links(list_url)
    results = []

    total = len(links)

    if total == 0:
        logging.warning("No links found — site likely blocking.")
        return results

    for i, link in enumerate(links, start=1):

        result = scrape_profile(link, save_dir)
        if result:
            results.append(result)

        percent = int((i / total) * 100)
        progress_callback(percent, f"{label}: {percent}%")

        time.sleep(1)

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
