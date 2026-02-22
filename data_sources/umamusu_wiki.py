from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.crawler import SafeCrawler

BASE = "https://umamusu.wiki"

TRAINEE_INDEX = BASE + "/Game:List_of_Trainees"
SUPPORT_INDEX = BASE + "/Game:List_of_Support_Cards"


def extract_internal_links(base, html):
    soup = BeautifulSoup(html, "lxml")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            full = urljoin(base, href)
            if base in full:
                links.add(full)

    return list(links)


def crawl_detail_pages(crawler, index_url):
    html = crawler.get(index_url)
    if not html:
        return []

    detail_links = extract_internal_links(BASE, html)
    results = []

    for link in detail_links:
        if "Game:" in link:
            continue

        page = crawler.get(link)
        if not page:
            continue

        soup = BeautifulSoup(page, "lxml")

        title = soup.find("h1")
        if not title:
            continue

        name = title.text.strip()

        img = soup.find("img")
        image_url = None
        if img and img.get("src"):
            image_url = img["src"]
            if image_url.startswith("//"):
                image_url = "https:" + image_url
            elif image_url.startswith("/"):
                image_url = urljoin(BASE, image_url)

        results.append({
            "name": name,
            "image": image_url,
            "source": "umamusu_wiki"
        })

    return results


def fetch_all():
    crawler = SafeCrawler(BASE)
    horses = crawl_detail_pages(crawler, TRAINEE_INDEX)
    cards = crawl_detail_pages(crawler, SUPPORT_INDEX)
    return horses, cards
