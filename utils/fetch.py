import logging
from utils.dedupe import merge_unique
from data_sources import umamusumedb


def fetch_all_data(progress_callback=None):
    logging.info("Starting manual index crawl...")

    all_horses = []
    all_cards = []

    try:
        horses, cards = umamusumedb.fetch_all(progress_callback)
        all_horses.extend(horses)
        all_cards.extend(cards)
    except Exception as e:
        logging.error(f"umamusumedb failed: {e}")

    all_horses = merge_unique(all_horses)
    all_cards = merge_unique(all_cards)

    return all_horses, all_cards
