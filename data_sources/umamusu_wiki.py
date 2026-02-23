import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE = "https://umamusu.wiki"
TRAINEES_URL = BASE + "/Game:List_of_Trainees"
SUPPORT_URL = BASE + "/Game:List_of_Support_Cards"

HEADERS = {"User-Agent": "Mozilla/5.0"}


def extract_image(img):
    if not img:
        return None

    url = img.get("data-src") or img.get("src")
    if not url:
        return None

    if url.startswith("//"):
        url = "https:" + url
    elif url.startswith("/"):
        url = urljoin(BASE, url)

    return url


def parse_page(url, entry_type, progress_callback=None):

    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    tables = soup.find_all("table")
    results = []

    total = len(tables)

    for i, table in enumerate(tables, 1):

        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(f"Umamusu Wiki ({entry_type}) — {percent}%")

        rows = table.find_all("tr")

        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 1:
                continue

            name = cols[0].get_text(strip=True)
            if not name or len(name) < 3:
                continue

            img = cols[0].find("img")
            image = extract_image(img)

            results.append({
                "name": name,
                "image": image,
                "type": entry_type,
                "source": "umamusu_wiki"
            })

    return results


def fetch_all(progress_callback=None):

    horses = parse_page(
        TRAINEES_URL,
        "character",
        progress_callback
    )

    cards = parse_page(
        SUPPORT_URL,
        "support",
        progress_callback
    )

    return horses, cards
