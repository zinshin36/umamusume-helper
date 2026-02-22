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


def parse_table_page(html):
    soup = BeautifulSoup(html, "lxml")
    results = []

    table = soup.find("table")
    if not table:
        logging.warning("No table found on page.")
        return results

    rows = table.find_all("tr")

    for row in rows[1:]:  # Skip header
        cols = row.find_all("td")
        if not cols:
            continue

        # First column usually contains image + name
        first_col = cols[0]

        # Extract name
        link = first_col.find("a")
        if not link:
            continue

        name = link.get_text(strip=True)

        # Extract image
        img_tag = first_col.find("img")
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

        horses = parse_table_page(horses_html)
        cards = parse_table_page(cards_html)

        logging.info(f"Horses fetched: {len(horses)}")
        logging.info(f"Cards fetched: {len(cards)}")
        logging.info(f"Fetch duration: {round(time.time() - start, 2)}s")

        return horses, cards

    except Exception as e:
        logging.exception("Error during fetch_all_data")
        raise e
