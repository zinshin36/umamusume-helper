import requests
import time
import logging
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser
from pathlib import Path

BASE = "https://umamusu.wiki"
HEADERS = {"User-Agent": "UmamusumeBuilderBot/1.0"}

HORSE_LIST = BASE + "/Game:List_of_Trainees"
SUPPORT_LIST = BASE + "/Game:List_of_Support_Cards"


def allowed_by_robots(url):
    rp = RobotFileParser()
    rp.set_url(BASE + "/robots.txt")
    rp.read()
    return rp.can_fetch("*", url)


def get_character_links(list_url):
    r = requests.get(list_url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/wiki/") and ":" not in href:
            full = urljoin(BASE, href)
            links.append(full)

    return list(set(links))


def extract_image(page_url):
    r = requests.get(page_url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(r.text, "html.parser")

    infobox = soup.find("table", class_="infobox")
    if not infobox:
        return None

    img = infobox.find("img")
    if not img:
        return None

    src = img.get("src")
    if src.startswith("//"):
        return "https:" + src
    return urljoin(BASE, src)


def download_image(url, save_dir: Path, name):
    filename = name.replace("/", "_").replace(" ", "_") + ".png"
    path = save_dir / filename

    if path.exists():
        return str(path)

    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        with open(path, "wb") as f:
            f.write(r.content)
        return str(path)
    return None


def crawl_category(list_url, save_dir: Path, progress_callback, label):
    logging.info(f"Crawling {list_url}")

    if not allowed_by_robots(list_url):
        logging.warning(f"Blocked by robots.txt: {list_url}")
        return []

    links = get_character_links(list_url)
    results = []

    total = len(links)

    for i, link in enumerate(links):
        percent = int((i / total) * 100)
        progress_callback(percent, f"Crawling {label}: {percent}%")

        time.sleep(1)  # respectful delay

        img_url = extract_image(link)
        if not img_url:
            continue

        name = link.split("/")[-1]
        path = download_image(img_url, save_dir, name)

        if path:
            results.append({"name": name, "image": path})

    return results


def crawl_all(base_dir: Path, progress_callback):
    horse_dir = base_dir / "data" / "images" / "horses"
    support_dir = base_dir / "data" / "images" / "support"

    horses = crawl_category(HORSE_LIST, horse_dir, progress_callback, "Horses")
    cards = crawl_category(SUPPORT_LIST, support_dir, progress_callback, "Support")

    logging.info(f"Crawl complete. Horses: {len(horses)} Cards: {len(cards)}")

    return {
        "horses": horses,
        "cards": cards
    }
