import logging

# Blacklist for cards
blacklist = set()

# Stat priority by horse type
STAT_PRIORITY = {
    "Front Runner": ["Speed", "Stamina", "Power", "Wit"],
    "Sprinter": ["Speed", "Power", "Stamina", "Wit"],
    "Stamina": ["Stamina", "Speed", "Power", "Wit"],
    "Power": ["Power", "Speed", "Stamina", "Wit"]
}

def find_horse(horse_name, horses):
    """Return all horse objects matching a name (partial match for versions)"""
    return [h for h in horses if horse_name.lower() in h['name'].lower()]

def recommend_cards_for_horse(horse, cards):
    """Return all valid cards for a horse, filtered by blacklist"""
    return [c for c in cards if c['type'] in STAT_PRIORITY.get(horse['type'], []) and c['name'] not in blacklist]

def build_deck(horse, cards, deck_size=6):
    """Return top cards for a horse"""
    valid_cards = recommend_cards_for_horse(horse, cards)
    priority = STAT_PRIORITY.get(horse['type'], [])
    valid_cards.sort(key=lambda x: priority.index(x['type']) if x['type'] in priority else 10)
    return valid_cards[:deck_size]

def recommend_races(horse):
    """Return recommended race distances"""
    return horse.get('distances', [])
