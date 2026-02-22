from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.crawler import SafeCrawler

BASE = "https://umamusu.wiki"
TRAINEES = BASE + "/Game:List_of_Trainees"
SUPPORT = BASE + "/Game:List_of_Support_Cards"


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
            "source": "umamusu_wiki"
        })

    return results


def fetch_all():
    crawler = SafeCrawler(BASE)

    horses = crawl_section(crawler, TRAINEES, "character")
    cards = crawl_section(crawler, SUPPORT, "support")

    return horses, cards
