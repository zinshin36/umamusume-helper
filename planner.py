import itertools
import math


RARITY_WEIGHT = {
    "SSR": 400,
    "SR": 250,
    "R": 50
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


def score_card(card, horse):

    if card.get("blacklisted"):
        return -999999

    rarity_score = RARITY_WEIGHT.get(card.get("rarity"), 0)

    preferred = horse_preferred_stat(horse)

    stat_bonus = 150 if card.get("type") == preferred else 40

    training_bonus = card.get("training_bonus", 0) * 4
    event_bonus = card.get("event_bonus", 0) * 3
    bond_bonus = card.get("initial_bond", 0) * 2

    skill_value = len(card.get("skills", [])) * 35

    return (
        rarity_score +
        stat_bonus +
        training_bonus +
        event_bonus +
        bond_bonus +
        skill_value
    )


def score_deck(deck, horse):

    total = sum(score_card(c, horse) for c in deck)

    type_count = {}
    for c in deck:
        t = c["type"]
        type_count[t] = type_count.get(t, 0) + 1

    # punish mono-type spam
    for count in type_count.values():
        if count > 4:
            total -= 300

    # skill overlap penalty
    seen = set()
    for c in deck:
        for skill in c.get("skills", []):
            if skill in seen:
                total -= 60
            seen.add(skill)

    return total


def recommend_deck(horse, scenario, cards):

    available = [c for c in cards if not c.get("blacklisted")]

    if len(available) < 6:
        return []

    scored = sorted(
        available,
        key=lambda c: score_card(c, horse),
        reverse=True
    )[:50]

    best_score = -math.inf
    best_deck = None

    for combo in itertools.combinations(scored, 6):
        s = score_deck(combo, horse)
        if s > best_score:
            best_score = s
            best_deck = combo

    return list(best_deck)
