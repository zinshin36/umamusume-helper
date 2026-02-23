import logging
from utils.dedupe import merge_unique
from data_sources import (
    umamusu_wiki,
    umamusumedb,
    umamusume_run,
    gametora
)


def fetch_all_data(progress_callback=None):

    all_horses = []
    all_cards = []

    sources = [
        ("Umamusu Wiki", umamusu_wiki.fetch_all),
        ("UmamusumeDB", umamusumedb.fetch_all),
        ("Umamusume Run", umamusume_run.fetch_all),
        ("GameTora", gametora.fetch_all),
    ]

    total_sources = len(sources)

    for index, (name, fetch_func) in enumerate(sources, 1):

        if progress_callback:
            percent = int((index - 1) / total_sources * 100)
            progress_callback(f"Fetching from {name} — {percent}%")

        try:
            horses, cards = fetch_func(progress_callback)
            all_horses.extend(horses)
            all_cards.extend(cards)
        except Exception as e:
            logging.warning(f"{name} failed: {e}")

    if progress_callback:
        progress_callback("Deduplicating data — 95%")

    all_horses = merge_unique(all_horses)
    all_cards = merge_unique(all_cards)

    if progress_callback:
        progress_callback("Complete — 100%")

    return all_horses, all_cards
