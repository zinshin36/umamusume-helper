import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://umamusu.wiki"
TRAINEES_URL = BASE + "/Game:List_of_Trainees"
SUPPORT_URL = BASE + "/Game:List_of_Support_Cards"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def parse_table(url, entry_type, progress_callback=None):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table")

    results = []

    total_tables = len(tables)

    for index, table in enumerate(tables, 1):

        if progress_callback:
            percent = int((index / total_tables) * 100)
            progress_callback(f"Umamusu Wiki ({entry_type}) — {percent}%")

        rows = table.find_all("tr")

        for row in rows[1:]:
            cols = row.find_all("td")
            if not cols:
                continue

            name_cell = cols[0]
            name = name_cell.get_text(strip=True)

            img_tag = name_cell.find("img")
            image_url = None

            if img_tag and img_tag.get("src"):
                image_url = img_tag["src"]
                if image_url.startswith("/"):
                    image_url = urljoin(BASE, image_url)

            if name:
                results.append({
                    "name": name,
                    "image": image_url,
                    "type": entry_type,
                    "source": "umamusu_wiki"
                })

    return results


def fetch_all(progress_callback=None):

    horses = parse_table(
        TRAINEES_URL,
        "character",
        progress_callback
    )

    cards = parse_table(
        SUPPORT_URL,
        "support",
        progress_callback
    )

    return horses, cards
