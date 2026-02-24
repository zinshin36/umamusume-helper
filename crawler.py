import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from pathlib import Path
import cloudscraper

BASE = "https://umamusu.wiki"

HORSE_LIST = BASE + "/Game:List_of_Trainees"
SUPPORT_LIST = BASE + "/Game:List_of_Support_Cards"

# Cloudflare-safe session
scraper = cloudscraper.create_scraper(
    browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    }
)


def get_character_links(list_url):
    logging.info(f"Fetching list page: {list_url}")

    r = scraper.get(list_url, timeout=60)

    if r.status_code != 200:
        logging.warning(f"Failed request: {r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "lxml")

    links = []

    # Find all character links in page content
    content = soup.find("div", {"id": "mw-content-text"})
    if not content:
        logging.warning("No content div found")
        return []

    for a in content.find_all("a", href=True):
        href = a["href"]

        if not href.startswith("/wiki/"):
            continue

        if ":" in href:
            continue

        full = urljoin(BASE, href)
        links.append(full)

    links = list(set(links))

    logging.info(f"Found {len(links)} links")
    return links


def scrape_profile(url, save_dir: Path):
    try:
        r = scraper.get(url, timeout=60)

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

        filename = name.replace("/", "_").replace(" ", "_") + ".png"
        path = save_dir / filename

        if not path.exists():
            img_data = scraper.get(img_url, timeout=60)
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
        logging.warning("No links found — Cloudflare likely blocking.")
        return results

    for i, link in enumerate(links, start=1):

        result = scrape_profile(link, save_dir)
        if result:
            results.append(result)

        percent = int((i / total) * 100)
        progress_callback(percent, f"{label}: {percent}%")

        # Slow crawl (you said speed doesn't matter)
        time.sleep(2)

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
