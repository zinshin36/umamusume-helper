import logging
from utils.dedupe import merge_unique
from data_sources import umamusu_wiki, umamusume_run, gametora, umamusumedb


def fetch_all_data():
    logging.info("Starting multi-site manual index crawl...")

    all_horses = []
    all_cards = []

    for source in [umamusu_wiki, umamusume_run, gametora, umamusumedb]:
        try:
            horses, cards = source.fetch_all()
            all_horses.extend(horses)
            all_cards.extend(cards)
        except Exception as e:
            logging.error(f"{source.__name__} failed: {e}")

    all_horses = merge_unique(all_horses)
    all_cards = merge_unique(all_cards)

    logging.info(f"Total Horses: {len(all_horses)}")
    logging.info(f"Total Cards: {len(all_cards)}")

    return all_horses, all_cards
