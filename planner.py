import math

# --------------------------------------------
# SCENARIO META
# --------------------------------------------

SCENARIO_META = {
    "URA": {"Speed": 3, "Stamina": 2, "Power": 1},
    "Aoharu": {"Speed": 2, "Power": 2, "Wisdom": 2},
    "Grand Live": {"Speed": 3, "Wisdom": 2},
    "Make a New Track": {"Speed": 2, "Power": 2, "Stamina": 1},
    "Project L'Arc": {"Speed": 3, "Wisdom": 3}
}

# --------------------------------------------
# TRAINING SIMULATION
# --------------------------------------------

def simulate_training(card, focus_weights):

    base = focus_weights.get(card["type"], 1)

    rarity_bonus = 1.5 if card["rarity"] == "SSR" else 1.2
    event_bonus = 1 + (card.get("event_bonus", 0) / 100)

    return base * rarity_bonus * event_bonus


# --------------------------------------------
# SKILL STACKING CHECK
# --------------------------------------------

def unique_skill_score(card, chosen_skills):

    score = 0
    for skill in card.get("skills", []):
        if skill not in chosen_skills:
            score += 10
    return score


# --------------------------------------------
# MAIN OPTIMIZER
# --------------------------------------------

def recommend_deck(horse, scenario, cards):

    focus = SCENARIO_META.get(scenario, {"Speed": 3})

    scored = []
    chosen_skills = set()

    for card in cards:

        score = 0

        # Tier weighting
        if card["rarity"] == "SSR":
            score += 100
        elif card["rarity"] == "SR":
            score += 40

        # Training efficiency
        training_score = simulate_training(card, focus)
        score += training_score * 50

        # Event bonus
        score += card.get("event_bonus", 0) * 2

        # Horse synergy
        if card["type"] == horse.get("preferred_stat"):
            score += 60

        # Unique skill stacking
        skill_score = unique_skill_score(card, chosen_skills)
        score += skill_score

        scored.append((score, card))

    scored.sort(key=lambda x: x[0], reverse=True)

    final_deck = []

    for score, card in scored:

        if len(final_deck) >= 6:
            break

        # Avoid overstacking same type
        type_count = sum(1 for c in final_deck if c["type"] == card["type"])
        if type_count >= 3:
            continue

        final_deck.append(card)
        for skill in card.get("skills", []):
            chosen_skills.add(skill)

    return final_deck
