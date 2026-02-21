import requests
from bs4 import BeautifulSoup
import json
import os
from urllib.parse import urljoin
from config import HORSES_PAGE, CARDS_PAGE, CACHE_FILE

BASE_URL = "https://umamusu.wiki"

os.makedirs("data/images", exist_ok=True)

def download_image(image_url, filename):
    try:
        response = requests.get(image_url, stream=True, timeout=10)
        if response.status_code == 200:
            with open(filename, "wb") as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            return filename
    except:
        pass
    return None

def scrape_category(page_url):
    r = requests.get(page_url, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")

    entries = []

    for link in soup.select("li.category-page__member > a"):
        name = link.text.strip()
        relative_url = link["href"]
        full_url = urljoin(BASE_URL, relative_url)

        image_path = scrape_image_from_page(full_url, name)

        entries.append({
            "name": name,
            "url": full_url,
            "image": image_path
        })

    return entries

def scrape_image_from_page(page_url, name):
    try:
        r = requests.get(page_url, timeout=15)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")

        img = soup.select_one("table.infobox img")
        if img:
            img_url = urljoin(BASE_URL, img["src"])
            safe_name = name.replace("/", "_").replace(" ", "_")
            local_path = f"data/images/{safe_name}.png"
            return download_image(img_url, local_path)
    except:
        pass
    return None

def fetch_data():
    data = {"horses": [], "cards": []}

    try:
        data["horses"] = scrape_category(HORSES_PAGE)
        data["cards"] = scrape_category(CARDS_PAGE)

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        return data

    except Exception as e:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return data
