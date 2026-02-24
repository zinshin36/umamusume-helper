import requests
import time
import logging
import json
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://umamusu.wiki/"
TRAINEES_PATH = "Game:List_of_Trainees"
SUPPORT_PATH = "Game:List_of_Support_Cards"

CRAWL_DELAY = 2  # Respect robots.txt

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0 Safari/537.36"
}


def build_url(path: str) -> str:
    """Ensure we always return a full absolute URL."""
    return urljoin(BASE_URL, path)


def fetch_page(url: str):
    logging.info(f"Fetching: {url}")

    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {e}")
        return None


def extract_links(html: str):
    soup = BeautifulSoup(html, "lxml")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        # Only grab internal Game pages
        if href.startswith("/Game:") and not "#" in href:
            full_url = urljoin(BASE_URL, href)
            links.append(full_url)

    return list(set(links))


def crawl():
    logging.info("Starting crawl")

    data = {
        "horses": [],
        "cards": []
    }

    # Build correct URLs
    trainees_url = build_url(TRAINEES_PATH)
    support_url = build_url(SUPPORT_PATH)

    # =========================
    # Crawl Trainees
    # =========================
    html = fetch_page(trainees_url)

    if html:
        links = extract_links(html)
        logging.info(f"Found {len(links)} trainee links")

        for link in links:
            data["horses"].append(link)
            time.sleep(CRAWL_DELAY)

    time.sleep(CRAWL_DELAY)

    # =========================
    # Crawl Support Cards
    # =========================
    html = fetch_page(support_url)

    if html:
        links = extract_links(html)
        logging.info(f"Found {len(links)} support links")

        for link in links:
            data["cards"].append(link)
            time.sleep(CRAWL_DELAY)

    # =========================
    # Save JSON
    # =========================
    try:
        with open("data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logging.info(
            f"Crawl complete. Horses: {len(data['horses'])} "
            f"Cards: {len(data['cards'])}"
        )
    except Exception as e:
        logging.error(f"Failed to write data.json: {e}")
