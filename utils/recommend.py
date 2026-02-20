# Blacklist for cards
blacklist = set()

# Stat priority by horse type
STAT_PRIORITY = {
    "Front Runner": ["Speed", "Stamina", "Power", "Wit"],
    "Sprinter": ["Speed", "Power", "Stamina", "Wit"],
    "Stamina": ["Stamina", "Speed", "Power", "Wit"],
    "Power": ["Power", "Speed", "Stamina", "Wit"]
}

def recommend_cards(horse_name, horses, cards):
    """Return all valid cards for a horse, filtered by blacklist"""
    recommended = []
    horse_type = next((h['type'] for h in horses if h['name'].lower() == horse_name.lower()), None)
    if not horse_type:
        return []

    for c in cards:
        if c['type'] in STAT_PRIORITY.get(horse_type, []) and c['name'] not in blacklist:
            recommended.append(c)
    return recommended

def build_deck(horse_name, horses, cards, deck_size=6):
    """Build a top deck of cards based on horse type"""
    valid_cards = recommend_cards(horse_name, horses, cards)
    horse_type = next((h['type'] for h in horses if h['name'].lower() == horse_name.lower()), None)
    if not horse_type:
        return []

    priority = STAT_PRIORITY.get(horse_type, [])
    # Sort by stat priority (Speed > Stamina > Power > Wit)
    valid_cards.sort(key=lambda x: priority.index(x['type']) if x['type'] in priority else 10)
    return valid_cards[:deck_size]

def recommend_races(horse_name, horses):
    """Return recommended race distances for a horse"""
    horse = next((h for h in horses if h['name'].lower() == horse_name.lower()), None)
    return horse['distances'] if horse else []
