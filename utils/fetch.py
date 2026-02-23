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
            progress_callback(f"{name} — {percent}%")

        try:
            horses, cards = fetch_func(progress_callback)
            all_horses.extend(horses)
            all_cards.extend(cards)
        except Exception:
            continue

    # Deduplicate by name
    unique_horses = {}
    for h in all_horses:
        key = h.get("name", "").strip().lower()
        if key:
            unique_horses[key] = h

    unique_cards = {}
    for c in all_cards:
        key = c.get("name", "").strip().lower()
        if key:
            unique_cards[key] = c

    if progress_callback:
        progress_callback("Complete — 100%")

    return list(unique_horses.values()), list(unique_cards.values())
