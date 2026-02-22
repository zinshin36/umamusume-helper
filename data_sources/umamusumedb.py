from bs4 import BeautifulSoup
from utils.crawler import SafeCrawler

BASE = "https://umamusumedb.com"


def fetch_characters():
    crawler = SafeCrawler(BASE)
    html = crawler.get(BASE)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []

    for link in soup.select("a"):
        href = link.get("href", "")
        if "/characters/" in href:
            name = link.text.strip()
            results.append({
                "name": name,
                "image": None,
                "source": "umamusumedb"
            })

    return results
