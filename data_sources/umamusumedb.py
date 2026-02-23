import requests
from bs4 import BeautifulSoup
from pathlib import Path
import os

BASE = "https://umamusumedb.com"
SITEMAP = BASE + "/sitemap-0.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

IMAGE_DIR = Path("data/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def download_image(url, name):
    try:
        filename = name.replace(" ", "_").replace("/", "_") + ".png"
        path = IMAGE_DIR / filename

        if path.exists():
            return str(path)

        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code == 200:
            with open(path, "wb") as f:
                f.write(r.content)
            return str(path)
    except:
        pass

    return None


def clean_name(name):
    if " - " in name:
        name = name.split(" - ")[0]
    if "|" in name:
        name = name.split("|")[0]
    return name.strip()


def fetch_all(progress_callback=None):

    horses = []
    cards = []

    response = requests.get(SITEMAP, headers=HEADERS, timeout=20)
    soup = BeautifulSoup(response.text, "xml")
    urls = [loc.text for loc in soup.find_all("loc")]

    # REMOVE JAPANESE DUPLICATES
    urls = [u for u in urls if "/ja/" not in u]

    character_urls = [u for u in urls if "/characters/" in u]
    support_urls = [u for u in urls if "/support-cards/" in u]

    total = len(character_urls) + len(support_urls)
    processed = 0

    # ---------- HORSES ----------
    for url in character_urls:
        processed += 1

        if progress_callback:
            progress_callback(
                f"UmamusumeDB {int((processed/total)*100)}%"
            )

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            page = BeautifulSoup(r.text, "lxml")
        except:
            continue

        meta_title = page.find("meta", property="og:title")
        meta_img = page.find("meta", property="og:image")

        if not meta_title or not meta_img:
            continue

        name = clean_name(meta_title["content"])
        img_url = meta_img["content"]

        if not name or "Characters" in name:
            continue

        local_img = download_image(img_url, name)

        horses.append({
            "name": name,
            "image": local_img,
            "source": "umamusumedb"
        })

    # ---------- SUPPORT CARDS ----------
    for url in support_urls:
        processed += 1

        if progress_callback:
            progress_callback(
                f"UmamusumeDB {int((processed/total)*100)}%"
            )

        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            page = BeautifulSoup(r.text, "lxml")
        except:
            continue

        meta_title = page.find("meta", property="og:title")
        meta_img = page.find("meta", property="og:image")

        if not meta_title or not meta_img:
            continue

        name = clean_name(meta_title["content"])
        img_url = meta_img["content"]

        if not name or "Support Cards" in name:
            continue

        local_img = download_image(img_url, name)

        cards.append({
            "name": name,
            "image": local_img,
            "source": "umamusumedb"
        })

    return horses, cards
