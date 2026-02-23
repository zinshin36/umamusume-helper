def recommend_cards(horse_name, data):
    if not horse_name:
        return []

    cards = data.get("cards", [])
    blacklist = set(data.get("blacklist", []))

    # Simple placeholder logic:
    # Recommend cards not blacklisted
    recommendations = [
        card for card in cards
        if card["name"] not in blacklist
    ]

    return recommendations[:6]
