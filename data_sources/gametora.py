from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.crawler import SafeCrawler

BASE = "https://gametora.com"
INDEX = BASE + "/umamusume"


def fetch_all():
    crawler = SafeCrawler(BASE)

    html = crawler.get(INDEX)
    if not html:
        return [], []

    soup = BeautifulSoup(html, "lxml")

    horses = []
    cards = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/api/" in href or "/admin/" in href:
            continue

        if not href.startswith("/"):
            continue

        url = urljoin(BASE, href)
        page_html = crawler.get(url)
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

        if "support" in href.lower():
            cards.append({
                "name": name,
                "image": image_url,
                "type": "support",
                "source": "gametora"
            })
        else:
            horses.append({
                "name": name,
                "image": image_url,
                "type": "character",
                "source": "gametora"
            })

    return horses, cards
