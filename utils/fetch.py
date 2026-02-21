import logging
import time

def fetch_all_data():
    logging.info("Simulating data fetch...")

    # Simulate delay so progress is visible
    time.sleep(2)

    horses = [
        {"name": "Special Week", "rarity": "3★"},
        {"name": "Silence Suzuka", "rarity": "3★"},
        {"name": "Tokai Teio", "rarity": "3★"},
    ]

    cards = [
        {"name": "Kitasan Black", "type": "Speed"},
        {"name": "Fine Motion", "type": "Wisdom"},
        {"name": "Super Creek", "type": "Stamina"},
    ]

    logging.info("Data fetch completed successfully.")
    return horses, cards
