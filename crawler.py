import logging
from data_manager import load_data, save_data

def crawl_horses(progress_callback=None):
    data = load_data()

    # TODO: Replace with actual crawl
    # This is placeholder logic
    new_horses = []

    if new_horses:
        data["horses"].extend(new_horses)
        save_data(data)

    logging.info(f"Crawled horses. Total: {len(data['horses'])}")
    return data["horses"]

def crawl_support_cards(progress_callback=None):
    data = load_data()

    # TODO: Replace with real crawl logic
    new_cards = []

    if new_cards:
        data["cards"].extend(new_cards)
        save_data(data)

    logging.info(f"Crawled support cards. Total: {len(data['cards'])}")
    return data["cards"]
