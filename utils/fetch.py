import requests
import logging
import time

API_URL = "https://umamusu.wiki/api.php"

HEADERS = {
    "User-Agent": "UmamusumeHelper/1.0"
}


def api_get(params):
    params["format"] = "json"
    response = requests.get(API_URL, params=params, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.json()


def get_category_members(category_name):
    logging.info(f"Fetching category members: {category_name}")
    params = {
        "action": "query",
        "list": "categorymembers",
        "cmtitle": f"Category:{category_name}",
        "cmlimit": "500"
    }
    data = api_get(params)
    return data.get("query", {}).get("categorymembers", [])


def get_page_image(title):
    params = {
        "action": "query",
        "titles": title,
        "prop": "pageimages",
        "piprop": "original"
    }
    data = api_get(params)
    pages = data.get("query", {}).get("pages", {})
    for page in pages.values():
        if "original" in page:
            return page["original"]["source"]
    return None


def fetch_trainees():
    members = get_category_members("Trainees")
    results = []

    for member in members:
        title = member["title"]
        image_url = get_page_image(title)

        results.append({
            "name": title,
            "image": image_url
        })

    logging.info(f"Trainees fetched: {len(results)}")
    return results


def fetch_support_cards():
    members = get_category_members("Support_Cards")
    results = []

    for member in members:
        title = member["title"]
        image_url = get_page_image(title)

        results.append({
            "name": title,
            "image": image_url
        })

    logging.info(f"Support cards fetched: {len(results)}")
    return results


def fetch_all_data():
    start = time.time()
    logging.info("Starting full data fetch...")

    try:
        horses = fetch_trainees()
        cards = fetch_support_cards()

        logging.info(f"Fetch duration: {round(time.time() - start, 2)}s")
        return horses, cards

    except Exception:
        logging.exception("Error during fetch_all_data")
        raise
