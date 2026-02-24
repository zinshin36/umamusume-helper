import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def get_global_character_names():
    url = "https://gametora.com/umamusume/characters"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    names = set()

    for tag in soup.find_all("a"):
        href = tag.get("href", "")
        if "/umamusume/characters/" in href:
            name = tag.text.strip()
            if name:
                names.add(name.lower())

    return names


def get_global_support_names():
    url = "https://gametora.com/umamusume/supports"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")

    names = set()

    for tag in soup.find_all("a"):
        href = tag.get("href", "")
        if "/umamusume/supports/" in href:
            name = tag.text.strip()
            if name:
                names.add(name.lower())

    return names
