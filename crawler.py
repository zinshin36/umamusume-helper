import requests
from bs4 import BeautifulSoup
import os
import logging
from data_manager import load_data, save_data, IMAGE_FOLDER


HEADERS = {"User-Agent": "Mozilla/5.0"}


def download_image(url, filepath):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            with open(filepath, "wb") as f:
                f.write(r.content)
    except Exception as e:
        logging.error(f"Image download failed: {e}")


def crawl_horses(progress_callback=None, full_scan=True):

    data = load_data()
    existing = {h["name"] for h in data["horses"]}

    url = "https://umamusumedb.com/characters"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    found = 0

    for img in soup.select("img"):
        name = img.get("alt")
        src = img.get("src")

        if not name or not src:
            continue

        if not full_scan and name in existing:
            continue

        if name not in existing:
            filename = name.replace(" ", "_").replace("/", "_") + ".png"
            filepath = os.path.join(IMAGE_FOLDER, filename)

            if not os.path.exists(filepath):
                download_image(src, filepath)

            data["horses"].append({
                "name": name,
                "image": filepath,
                "source": "umamusumedb"
            })

            found += 1

        if progress_callback:
            progress_callback()

    save_data(data)
    logging.info(f"Horses crawl complete. Added: {found}")
    return found


def crawl_support_cards(progress_callback=None, full_scan=True):

    data = load_data()
    existing = {c["name"] for c in data["cards"]}

    url = "https://umamusumedb.com/support-cards"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    found = 0

    for img in soup.select("img"):
        name = img.get("alt")
        src = img.get("src")

        if not name or not src:
            continue

        if not full_scan and name in existing:
            continue

        if name not in existing:
            filename = name.replace(" ", "_").replace("/", "_") + ".png"
            filepath = os.path.join(IMAGE_FOLDER, filename)

            if not os.path.exists(filepath):
                download_image(src, filepath)

            data["cards"].append({
                "name": name,
                "image": filepath,
                "source": "umamusumedb"
            })

            found += 1

        if progress_callback:
            progress_callback()

    save_data(data)
    logging.info(f"Support cards crawl complete. Added: {found}")
    return found
