import os
import requests
from bs4 import BeautifulSoup
import logging

BASE_URL = "https://umamusume.fandom.com"

def fetch_data(progress_callback=None):
    horses = []
    cards = []

    os.makedirs("images/horses", exist_ok=True)
    os.makedirs("images/cards", exist_ok=True)

    # ---- Fetch Horses Page ----
    try:
        url = BASE_URL + "/wiki/Category:Playable_Uma_Musume"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        links = soup.select(".category-page__member-link")
        total = len(links)

        for i, link in enumerate(links):
            name = link.text.strip()
            page_url = BASE_URL + link.get("href")

            page = requests.get(page_url)
            page_soup = BeautifulSoup(page.text, "lxml")

            img_tag = page_soup.select_one(".pi-image-thumbnail")
            if img_tag:
                img_url = img_tag.get("src")
                img_data = requests.get(img_url).content

                img_path = f"images/horses/{name}.png"
                with open(img_path, "wb") as f:
                    f.write(img_data)

                horses.append({
                    "name": name,
                    "image_path": img_path
                })

            if progress_callback:
                progress_callback(int((i / total) * 50))

    except Exception as e:
        logging.error(str(e))

    # ---- Fetch Support Cards ----
    try:
        url = BASE_URL + "/wiki/Category:Support_Cards"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        links = soup.select(".category-page__member-link")
        total = len(links)

        for i, link in enumerate(links):
            name = link.text.strip()
            page_url = BASE_URL + link.get("href")

            page = requests.get(page_url)
            page_soup = BeautifulSoup(page.text, "lxml")

            img_tag = page_soup.select_one(".pi-image-thumbnail")
            if img_tag:
                img_url = img_tag.get("src")
                img_data = requests.get(img_url).content

                img_path = f"images/cards/{name}.png"
                with open(img_path, "wb") as f:
                    f.write(img_data)

                cards.append({
                    "name": name,
                    "image_path": img_path
                })

            if progress_callback:
                progress_callback(50 + int((i / total) * 50))

    except Exception as e:
        logging.error(str(e))

    if progress_callback:
        progress_callback(100)

    return {"horses": horses, "cards": cards}
