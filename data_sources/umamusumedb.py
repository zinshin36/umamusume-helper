import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import html

BASE = "https://umamusumedb.com"
SITEMAP = BASE + "/sitemap-0.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def clean_title(title):
    title = html.unescape(title)
    if "|" in title:
        title = title.split("|")[0].strip()
    return title


def extract_image(soup):
    # Use og:image (correct structured image)
    meta = soup.find("meta", property="og:image")
    if not meta:
        return None

    url = meta.get("content")
    if not url:
        return None

    if "og-image.png" in url:
        return None

    return url


def fetch_all(progress_callback=None):

    response = requests.get(SITEMAP, headers=HEADERS, timeout=20)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "xml")
    urls = [loc.text for loc in soup.find_all("loc")]

    horses = []
    cards = []

    # Filter only structured URLs
    character_urls = [u for u in urls if "/characters/" in u]
    support_urls = [u for u in urls if "/support/" in u]

    total = len(character_urls) + len(support_urls)
    processed = 0

    # ---- CHARACTERS ----
    for url in character_urls:
        processed += 1

        if progress_callback:
            percent = int((processed / total) * 100)
            progress_callback(f"UmamusumeDB — {percent}%")

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except:
            continue

        page = BeautifulSoup(r.text, "lxml")

        title_tag = page.find("meta", property="og:title")
        if not title_tag:
            continue

        name = clean_title(title_tag.get("content", ""))

        image = extract_image(page)

        if not name:
            continue

        horses.append({
            "name": name,
            "image": image,
            "source": "umamusumedb"
        })

    # ---- SUPPORT CARDS ----
    for url in support_urls:
        processed += 1

        if progress_callback:
            percent = int((processed / total) * 100)
            progress_callback(f"UmamusumeDB — {percent}%")

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            r.raise_for_status()
        except:
            continue

        page = BeautifulSoup(r.text, "lxml")

        title_tag = page.find("meta", property="og:title")
        if not title_tag:
            continue

        name = clean_title(title_tag.get("content", ""))

        image = extract_image(page)

        if not name:
            continue

        cards.append({
            "name": name,
            "image": image,
            "source": "umamusumedb"
        })

    return horses, cards
