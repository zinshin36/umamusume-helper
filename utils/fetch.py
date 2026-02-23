import json
import os

from utils.paths import DATA_DIR
from utils.logger import logger
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

    total = len(sources)

    for i, (name, func) in enumerate(sources, 1):

        if progress_callback:
            percent = int((i - 1) / total * 100)
            progress_callback(f"{name} — {percent}%")

        try:
            horses, cards = func(progress_callback)
            all_horses.extend(horses)
            all_cards.extend(cards)
            logger.info(f"{name} fetched")
        except Exception as e:
            logger.error(f"{name} failed: {e}")

    # Deduplicate
    unique_horses = {h["name"].lower(): h for h in all_horses if h.get("name")}
    unique_cards = {c["name"].lower(): c for c in all_cards if c.get("name")}

    output = {
        "horses": list(unique_horses.values()),
        "cards": list(unique_cards.values())
    }

    output_path = os.path.join(DATA_DIR, "data.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    if progress_callback:
        progress_callback("Complete — 100%")

    logger.info("Data saved")

    return output["horses"], output["cards"]
