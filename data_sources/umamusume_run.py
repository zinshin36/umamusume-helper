from bs4 import BeautifulSoup
from utils.crawler import SafeCrawler

BASE = "https://umamusume.run"


def fetch_support_cards():
    crawler = SafeCrawler(BASE)
    url = BASE + "/database/support-cards"
    html = crawler.get(url)
    if not html:
        return []

    soup = BeautifulSoup(html, "lxml")
    results = []

    for card in soup.select("a"):
        name = card.text.strip()
        if name:
            results.append({
                "name": name,
                "image": None,
                "source": "umamusume.run"
            })

    return results
