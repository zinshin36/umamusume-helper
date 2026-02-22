from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils.crawler import SafeCrawler

BASE = "https://umamusume.run"

CHAR_INDEX = BASE + "/database"
SUPPORT_INDEX = BASE + "/database/support-cards"


def extract_internal_links(base, html):
    soup = BeautifulSoup(html, "lxml")
    links = set()

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if href.startswith("/"):
            full = urljoin(base, href)
            if urlparse(full).netloc == urlparse(base).netloc:
                links.add(full)

    return list(links)


def extract_basic_page_data(base, html):
    soup = BeautifulSoup(html, "lxml")

    title_tag = soup.find("h1")
    if not title_tag:
        return None

    name = title_tag.get_text(strip=True)

    img_tag = soup.find("img")
    image_url = None

    if img_tag and img_tag.get("src"):
        image_url = img_tag["src"]

        if image_url.startswith("//"):
            image_url = "https:" + image_url
        elif image_url.startswith("/"):
            image_url = urljoin(base, image_url)

    return name, image_url


def crawl_section(crawler, index_url, entry_type):
    html = crawler.get(index_url)
    if not html:
        return []

    links = extract_internal_links(BASE, html)
    results = []

    for link in links:
        page_html = crawler.get(link)
        if not page_html:
            continue

        data = extract_basic_page_data(BASE, page_html)
        if not data:
            continue

        name, image_url = data

        results.append({
            "name": name,
            "image": image_url,
            "type": entry_type,
            "source": "umamusume_run"
        })

    return results


def fetch_all():
    crawler = SafeCrawler(BASE)

    horses = crawl_section(crawler, CHAR_INDEX, "character")
    cards = crawl_section(crawler, SUPPORT_INDEX, "support")

    return horses, cards
