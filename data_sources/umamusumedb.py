from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.crawler import SafeCrawler

BASE = "https://umamusumedb.com"
SITEMAP = BASE + "/sitemap-0.xml"


def fetch_all(progress_callback=None):
    crawler = SafeCrawler(BASE, progress_callback, "umamusumedb")

    sitemap_xml = crawler.get(SITEMAP)
    if not sitemap_xml:
        return [], []

    soup = BeautifulSoup(sitemap_xml, "xml")
    urls = [loc.text for loc in soup.find_all("loc")]

    horses = []
    cards = []

    total = len(urls)

    for i, url in enumerate(urls, 1):
        crawler.report_progress(i, total)

        if "/api/" in url or "/admin/" in url:
            continue

        html = crawler.get(url)
        if not html:
            continue

        page = BeautifulSoup(html, "lxml")
        title = page.find("h1")

        if not title:
            continue

        name = title.get_text(strip=True)

        img = page.find("img")
        image_url = None

        if img and img.get("src"):
            image_url = img["src"]
            if image_url.startswith("/"):
                image_url = urljoin(BASE, image_url)

        if "support" in url.lower():
            cards.append({
                "name": name,
                "image": image_url,
                "type": "support",
                "source": "umamusumedb"
            })
        else:
            horses.append({
                "name": name,
                "image": image_url,
                "type": "character",
                "source": "umamusumedb"
            })

    return horses, cards
