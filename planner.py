import itertools
import math


RARITY_WEIGHT = {
    "SSR": 200,
    "SR": 120,
    "R": 30
}


def horse_preferred_stat(horse):

    growths = {
        "Speed": horse.get("speed_growth", 0),
        "Stamina": horse.get("stamina_growth", 0),
        "Power": horse.get("power_growth", 0),
        "Guts": horse.get("guts_growth", 0),
        "Wisdom": horse.get("wisdom_growth", 0)
    }

    return max(growths, key=growths.get)


def score_card(card, horse, scenario):

    if card.get("blacklisted"):
        return -999999

    rarity_score = RARITY_WEIGHT.get(card.get("rarity"), 0)

    preferred = horse_preferred_stat(horse)

    stat_bonus = 50 if card.get("type") == preferred else 10

    training_bonus = card.get("training_bonus", 0) * 2
    event_bonus = card.get("event_bonus", 0) * 1.5
    bond_bonus = card.get("initial_bond", 0)

    skill_value = len(card.get("skills", [])) * 20

    return (
        rarity_score +
        stat_bonus +
        training_bonus +
        event_bonus +
        bond_bonus +
        skill_value
    )


def score_deck(deck, horse, scenario):

    total = sum(score_card(c, horse, scenario) for c in deck)

    # penalize duplicate types >3
    type_count = {}
    for c in deck:
        t = c["type"]
        type_count[t] = type_count.get(t, 0) + 1

    for t, count in type_count.items():
        if count > 3:
            total -= 50

    # skill overlap penalty
    seen = set()
    for c in deck:
        for skill in c.get("skills", []):
            if skill in seen:
                total -= 30
            seen.add(skill)

    return total


def recommend_deck(horse, scenario, cards):

    available = [c for c in cards if not c.get("blacklisted")]

    if len(available) < 6:
        return []

    scored = sorted(
        available,
        key=lambda c: score_card(c, horse, scenario),
        reverse=True
    )[:40]

    best_score = -math.inf
    best_deck = None

    for combo in itertools.combinations(scored, 6):

        s = score_deck(combo, horse, scenario)

        if s > best_score:
            best_score = s
            best_deck = combo

    return list(best_deck)
