from data_manager import load_state


# Stat weight profiles
HORSE_TYPE_WEIGHTS = {
    "speed": {"speed": 3, "power": 1.5, "stamina": 1, "guts": 0.5, "wisdom": 1},
    "stamina": {"stamina": 3, "speed": 1.5, "power": 1.5, "guts": 1, "wisdom": 1},
    "power": {"power": 3, "speed": 2, "stamina": 1, "guts": 1, "wisdom": 1},
    "guts": {"guts": 3, "speed": 1.5, "power": 1.5, "stamina": 1, "wisdom": 1},
    "wisdom": {"wisdom": 3, "speed": 2, "power": 1, "stamina": 1, "guts": 1}
}


def calculate_card_score(card, weights, star_level):
    stats = card.get("stats", {})
    score = 0

    for stat, value in stats.items():
        weight = weights.get(stat.lower(), 1)
        score += value * weight

    # star multiplier
    score *= (1 + (star_level * 0.1))

    return score


def recommend_deck(horse, cards):
    state = load_state()
    blacklist = state["blacklist"]
    stars = state["stars"]

    # assume horse has a "type" field
    horse_type = horse.get("type", "speed").lower()
    weights = HORSE_TYPE_WEIGHTS.get(horse_type, HORSE_TYPE_WEIGHTS["speed"])

    scored = []

    for card in cards:
        if card["id"] in blacklist:
            continue

        star_level = stars.get(str(card["id"]), 0)
        score = calculate_card_score(card, weights, star_level)

        scored.append((score, card))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [c for _, c in scored[:6]]


def recommend_legacy(horse, horses):
    """
    Legacy scoring:
    Prefer same type
    Bonus for matching base stat focus
    """

    base_type = horse.get("type", "speed")

    scored = []

    for h in horses:
        if h["id"] == horse["id"]:
            continue

        score = 0

        if h.get("type") == base_type:
            score += 50

        if h.get("rarity", 1) >= 3:
            score += 20

        scored.append((score, h))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [h for _, h in scored[:3]]
