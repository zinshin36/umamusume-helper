import logging
from data_sources import umamusumedb, umamusume_run, gametora
from utils.dedupe import merge_unique


def fetch_all():
    logging.info("Fetching from all allowed sources...")

    all_items = []

    try:
        all_items += umamusumedb.fetch_characters()
    except Exception as e:
        logging.error(f"umamusumedb failed: {e}")

    try:
        all_items += umamusume_run.fetch_support_cards()
    except Exception as e:
        logging.error(f"umamusume.run failed: {e}")

    try:
        all_items += gametora.fetch_data()
    except Exception as e:
        logging.error(f"gametora failed: {e}")

    merged = merge_unique(all_items)

    logging.info(f"Total unique entries: {len(merged)}")
    return merged
