import requests
import xml.etree.ElementTree as ET

BASE = "https://umamusumedb.com"
SITEMAP = BASE + "/sitemap-0.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def fetch_all(progress_callback=None):

    response = requests.get(SITEMAP, headers=HEADERS, timeout=20)
    root = ET.fromstring(response.content)

    urls = [
        loc.text for loc in root.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
        if "/characters/" in loc.text.lower()
        or "/support" in loc.text.lower()
    ]

    horses = []
    cards = []

    total = len(urls)

    for i, url in enumerate(urls, 1):

        if progress_callback:
            percent = int((i / total) * 100)
            progress_callback(f"UmamusumeDB — {percent}%")

        response = requests.get(url, headers=HEADERS, timeout=20)
        html = response.text

        title = extract_meta(html, "og:title")
        image = extract_meta(html, "og:image")

        entry = {
            "name": title,
            "image": image,
            "source": "umamusumedb"
        }

        if "/support" in url.lower():
            cards.append(entry)
        else:
            horses.append(entry)

    return horses, cards


def extract_meta(html, prop):
    marker = f'property="{prop}" content="'
    start = html.find(marker)
    if start == -1:
        return None
    start += len(marker)
    end = html.find('"', start)
    return html[start:end]
