import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import json
import os

BASE_URL = "https://umamusu.wiki/"
TRAINEES_URL = urljoin(BASE_URL, "Game:List_of_Trainees")
SUPPORT_URL = urljoin(BASE_URL, "Game:List_of_Support_Cards")

CRAWL_DELAY = 2  # Respect robots.txt

HEADERS = {
    "User-Agent": "UmamusumeBuilderBot/1.0"
}

logging.basicConfig(
    filename="app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def fetch_page(url):
    logging.info(f"Fetching: {url}")
    response = requests.get(url, headers=HEADERS, timeout=30)

    if response.status_code != 200:
        logging.warning(f"Failed request: {response.status_code}")
        return None

    return response.text


def extract_links(html):
    soup = BeautifulSoup(html, "lxml")
    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/Game:") and ":" not in href[6:]:
            full_url = urljoin(BASE_URL, href)
            links.append(full_url)

    return list(set(links))


def crawl():
    logging.info("Starting crawl")

    data = {
        "horses": [],
        "cards": []
    }

    # Crawl trainees
    html = fetch_page(TRAINEES_URL)
    if html:
        links = extract_links(html)
        logging.info(f"Found {len(links)} trainee links")

        for link in links:
            data["horses"].append(link)
            time.sleep(CRAWL_DELAY)

    time.sleep(CRAWL_DELAY)

    # Crawl support cards
    html = fetch_page(SUPPORT_URL)
    if html:
        links = extract_links(html)
        logging.info(f"Found {len(links)} support card links")

        for link in links:
            data["cards"].append(link)
            time.sleep(CRAWL_DELAY)

    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    logging.info(
        f"Crawl complete. Horses: {len(data['horses'])} Cards: {len(data['cards'])}"
    )


if __name__ == "__main__":
    logging.info("Application started")
    crawl()
