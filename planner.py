import random

# Scenario meta ratios
SCENARIO_META = {
    "URA": {"Speed": 3, "Stamina": 2, "Power": 1},
    "Aoharu": {"Speed": 2, "Power": 2, "Wisdom": 2},
    "Grand Live": {"Speed": 3, "Wisdom": 2},
    "Make a New Track": {"Speed": 2, "Power": 2, "Stamina": 1},
    "Project L'Arc": {"Speed": 3, "Wisdom": 2}
}


def recommend_deck(horse, scenario, cards):

    stat_focus = SCENARIO_META.get(scenario, {"Speed": 3})

    scored_cards = []

    for card in cards:

        score = 0

        # Tier weighting
        if card.get("rarity") == "SSR":
            score += 50
        elif card.get("rarity") == "SR":
            score += 20

        # Type weighting
        card_type = card.get("type", "Speed")

        if card_type in stat_focus:
            score += stat_focus[card_type] * 20

        # Synergy bonus
        if horse.get("preferred_stat") == card_type:
            score += 30

        scored_cards.append((score, card))

    scored_cards.sort(key=lambda x: x[0], reverse=True)

    best = [c for _, c in scored_cards[:6]]

    return best
