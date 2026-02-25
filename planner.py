import itertools
import random

STAT_CAP = 1200
TURNS = 65

SCENARIO_MULT = {
    "URA": 1.0,
    "Aoharu": 1.1,
    "Grand Live": 1.2,
    "Make a New Track": 1.15,
    "Project L'Arc": 1.25
}


def simulate_training(deck, scenario):

    mult = SCENARIO_MULT.get(scenario, 1.0)

    stats = {"Speed":0,"Stamina":0,"Power":0,"Wisdom":0,"Guts":0}

    for _ in range(TURNS):

        card = random.choice(deck)

        base = 12 if card["rarity"] == "SSR" else 8
        gain = base * mult
        gain *= 1 + (card.get("event_bonus",0)/100)

        stats[card["type"]] += gain

    for k in stats:
        stats[k] = min(stats[k], STAT_CAP)

    return sum(stats.values())


def recommend_deck(horse, scenario, cards):

    pool = [c for c in cards if not c.get("blacklisted")]

    sorted_pool = sorted(pool, key=lambda c: 2 if c["rarity"]=="SSR" else 1, reverse=True)[:25]

    best_score = 0
    best_deck = []

    for combo in itertools.combinations(sorted_pool, 6):

        score = 0
        for _ in range(10):  # Monte Carlo 10 sims
            score += simulate_training(combo, scenario)

        if score > best_score:
            best_score = score
            best_deck = combo

    return list(best_deck)
