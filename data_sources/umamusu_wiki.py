import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://umamusu.wiki"
TRAINEES_URL = BASE + "/Game:List_of_Trainees"
SUPPORT_URL = BASE + "/Game:List_of_Support_Cards"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def extract_image(img_tag):
    if not img_tag:
        return None

    # prefer high quality
    image_url = img_tag.get("data-src") or img_tag.get("src")

    if not image_url:
        return None

    if image_url.startswith("//"):
        image_url = "https:" + image_url

    if image_url.startswith("/"):
        image_url = urljoin(BASE, image_url)

    return image_url


def parse_tables(url, entry_type, progress_callback=None):
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")
    tables = soup.find_all("table")

    results = []
    total_tables = len(tables)

    for t_index, table in enumerate(tables, 1):

        if progress_callback:
            percent = int((t_index / total_tables) * 100)
            progress_callback(f"Umamusu Wiki ({entry_type}) — {percent}%")

        rows = table.find_all("tr")

        for row in rows[1:]:
            cols = row.find_all("td")
            if not cols:
                continue

            name = cols[0].get_text(strip=True)
            if not name or len(name) < 2:
                continue

            img_tag = cols[0].find("img")
            image_url = extract_image(img_tag)

            results.append({
                "name": name,
                "image": image_url,
                "type": entry_type,
                "source": "umamusu_wiki"
            })

    return results


def fetch_all(progress_callback=None):

    horses = parse_tables(
        TRAINEES_URL,
        "character",
        progress_callback
    )

    cards = parse_tables(
        SUPPORT_URL,
        "support",
        progress_callback
    )

    return horses, cards
