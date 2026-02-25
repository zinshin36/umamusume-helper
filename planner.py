import itertools
import math

STAT_CAP = 1200

SCENARIO_MULTIPLIER = {
    "URA": 1.0,
    "Aoharu": 1.1,
    "Grand Live": 1.2,
    "Make a New Track": 1.15,
    "Project L'Arc": 1.25
}


def simulate_deck(deck, scenario):

    multiplier = SCENARIO_MULTIPLIER.get(scenario, 1.0)

    stats = {
        "Speed": 0,
        "Stamina": 0,
        "Power": 0,
        "Wisdom": 0,
        "Guts": 0
    }

    for card in deck:

        base_gain = 80 if card["rarity"] == "SSR" else 50

        gain = base_gain * multiplier

        gain *= 1 + (card.get("event_bonus", 0) / 100)

        stats[card["type"]] += gain

    # Cap clamp
    for k in stats:
        stats[k] = min(stats[k], STAT_CAP)

    total_score = sum(stats.values())

    return total_score


def recommend_deck(horse, scenario, cards):

    available = [c for c in cards if not c.get("blacklisted")]

    best_score = 0
    best_deck = []

    # Test top 30 strongest cards only (pre-sort by rarity)
    sorted_cards = sorted(
        available,
        key=lambda c: 2 if c["rarity"] == "SSR" else 1,
        reverse=True
    )[:30]

    for combo in itertools.combinations(sorted_cards, 6):

        # Avoid stacking more than 3 same type
        types = [c["type"] for c in combo]
        if any(types.count(t) > 3 for t in types):
            continue

        score = simulate_deck(combo, scenario)

        if score > best_score:
            best_score = score
            best_deck = combo

    return list(best_deck)
