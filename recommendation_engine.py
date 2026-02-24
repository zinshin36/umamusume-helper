from data_manager import load_state


def recommend(horse, cards):
    state = load_state()
    blacklist = state["blacklist"]
    stars = state["stars"]

    scored = []

    for card in cards:
        if card["id"] in blacklist:
            continue

        base_score = sum(card.get("stats", {}).values()) if card.get("stats") else 0
        star_bonus = stars.get(str(card["id"]), 0) * 10

        total = base_score + star_bonus

        scored.append((total, card))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [c for _, c in scored[:6]]
