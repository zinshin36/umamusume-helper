from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.crawler import SafeCrawler

BASE = "https://umamusume.run"
INDEX = BASE + "/database"
SUPPORT = BASE + "/database/support-cards"


def crawl_section(crawler, url, entry_type):
    html = crawler.get(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/api/" in href or "/admin/" in href:
            continue

        if not href.startswith("/"):
            continue

        full_url = urljoin(BASE, href)

        page_html = crawler.get(full_url)
        if not page_html:
            continue

        page = BeautifulSoup(page_html, "lxml")
        title = page.find("h1")

        if not title:
            continue

        name = title.get_text(strip=True)

        img = page.find("img")
        image_url = img["src"] if img and img.get("src") else None

        if image_url and image_url.startswith("/"):
            image_url = urljoin(BASE, image_url)

        results.append({
            "name": name,
            "image": image_url,
            "type": entry_type,
            "source": "umamusume_run"
        })

    return results


def fetch_all():
    crawler = SafeCrawler(BASE)

    horses = crawl_section(crawler, INDEX, "character")
    cards = crawl_section(crawler, SUPPORT, "support")

    return horses, cards
