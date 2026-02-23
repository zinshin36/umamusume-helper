import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from utils.storage import (
    ensure_directories,
    load_data,
    save_data,
    deduplicate,
    HORSE_IMG_DIR,
    SUPPORT_IMG_DIR
)

VALID_CARD_TIERS = ["SSR", "SR", "R"]


def is_valid_name(name):
    if not name:
        return False
    name = name.strip()
    if name.lower() in ["umamusumedb", "logo", "home"]:
        return False
    if len(name) < 3:
        return False
    return True


def download_image(url, save_dir, name):
    try:
        if not url.startswith("http"):
            return None

        filename = name.replace(" ", "_").replace("/", "_")
        path = os.path.join(save_dir, f"{filename}.png")

        if os.path.exists(path):
            return path

        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(path, "wb") as f:
                f.write(response.content)
            return path
    except:
        return None


def fetch_umamusu_wiki(progress_callback=None):
    horses = []
    cards = []

    base = "https://umamusu.wiki"

    pages = [
        ("Horses", "https://umamusu.wiki/Game:List_of_Trainees"),
        ("Support", "https://umamusu.wiki/Game:List_of_Support_Cards"),
    ]

    total_pages = len(pages)

    for index, (label, url) in enumerate(pages):
        if progress_callback:
            percent = int((index / total_pages) * 100)
            progress_callback(percent, f"Scanning {label} page...")

        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a"):
            name = link.get_text(strip=True)

            if not is_valid_name(name):
                continue

            img = link.find("img")
            if not img:
                continue

            img_url = img.get("src")
            if not img_url:
                continue

            img_url = urljoin(base, img_url)

            if label == "Horses":
                path = download_image(img_url, HORSE_IMG_DIR, name)
                if path:
                    horses.append({
                        "name": name,
                        "image": path,
                        "source": "umamusu_wiki"
                    })

            elif label == "Support":
                if not any(tier in name for tier in VALID_CARD_TIERS):
                    continue

                path = download_image(img_url, SUPPORT_IMG_DIR, name)
                if path:
                    cards.append({
                        "name": name,
                        "image": path,
                        "source": "umamusu_wiki"
                    })

    return horses, cards


def fetch_all_sites(progress_callback=None):
    ensure_directories()
    data = load_data()

    horses, cards = fetch_umamusu_wiki(progress_callback)

    data["horses"].extend(horses)
    data["cards"].extend(cards)

    data["horses"] = deduplicate(data["horses"])
    data["cards"] = deduplicate(data["cards"])

    save_data(data)

    if progress_callback:
        progress_callback(100, "Crawl complete")

    return len(data["horses"]), len(data["cards"])
