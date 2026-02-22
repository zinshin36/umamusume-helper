from bs4 import BeautifulSoup
from utils.crawler import SafeCrawler

BASE = "https://gametora.com"


def fetch_data():
    crawler = SafeCrawler(BASE)
    url = BASE + "/umamusume"
    html = crawler.get(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []

    for link in soup.select("a"):
        name = link.text.strip()
        if name:
            results.append({
                "name": name,
                "image": None,
                "source": "gametora"
            })

    return results
