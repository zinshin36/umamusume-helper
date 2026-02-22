from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from utils.crawler import SafeCrawler

BASE = "https://gametora.com"
INDEX = BASE + "/umamusume"


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


def fetch_all():
    crawler = SafeCrawler(BASE)

    html = crawler.get(INDEX)
    if not html:
        return [], []

    links = extract_internal_links(BASE, html)

    horses = []
    cards = []

    for link in links:
        page_html = crawler.get(link)
        if not page_html:
            continue

        data = extract_basic_page_data(BASE, page_html)
        if not data:
            continue

        name, image_url = data

        if "support" in link.lower():
            entry_type = "support"
            cards.append({
                "name": name,
                "image": image_url,
                "type": entry_type,
                "source": "gametora"
            })
        else:
            entry_type = "character"
            horses.append({
                "name": name,
                "image": image_url,
                "type": entry_type,
                "source": "gametora"
            })

    return horses, cards
