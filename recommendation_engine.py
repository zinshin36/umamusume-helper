from data_manager import load_state

SCENARIO_MODIFIERS = {
    "URA": {"speed": 1, "power": 1, "stamina": 1, "guts": 1, "wisdom": 1},
    "Aoharu": {"speed": 1.2, "power": 1.2, "stamina": 1, "guts": 1, "wisdom": 1},
    "Grand Live": {"wisdom": 1.3, "speed": 1.1, "power": 1, "stamina": 1, "guts": 1}
}


def recommend_deck(horse, cards, scenario):
    state = load_state()
    blacklist = state["blacklist"]
    stars = state["stars"]

    weights = SCENARIO_MODIFIERS.get(scenario, SCENARIO_MODIFIERS["URA"])

    scored = []

    for card in cards:
        if card["id"] in blacklist:
            continue

        star_level = stars.get(str(card["id"]), 0)

        score = 0
        for stat, value in card.get("stats", {}).items():
            modifier = weights.get(stat.lower(), 1)
            score += value * modifier

        score *= (1 + star_level * 0.15)

        scored.append((score, card))

    scored.sort(reverse=True, key=lambda x: x[0])
    return [c for _, c in scored[:6]]
