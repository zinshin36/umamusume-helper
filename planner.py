import itertools
import math


# ==========================================================
# META WEIGHTS
# ==========================================================

RARITY_WEIGHT = {
    "SSR": 100,
    "SR": 60,
    "R": 20
}

TYPE_WEIGHT = {
    "Speed": 1.2,
    "Stamina": 1.1,
    "Power": 1.15,
    "Guts": 0.9,
    "Wit": 1.0,
    "Intelligence": 1.0
}

SCENARIO_MULTIPLIER = {
    "URA": 1.0,
    "Aoharu": 1.05,
    "Grand Live": 1.1,
    "Make a New Track": 1.15,
    "Project L'Arc": 1.2
}

SKILL_BASE_VALUE = 15
EVENT_BONUS_WEIGHT = 0.8


# ==========================================================
# SKILL VALUE ESTIMATION
# ==========================================================

def evaluate_skills(card):
    skills = card.get("skills", [])
    return len(skills) * SKILL_BASE_VALUE


# ==========================================================
# CARD SCORING
# ==========================================================

def score_card(card, horse, scenario):

    if card.get("blacklisted"):
        return -999999

    rarity_score = RARITY_WEIGHT.get(card.get("rarity", "R"), 10)

    preferred = horse.get("preferred_stat", "Speed")
    type_bonus = TYPE_WEIGHT.get(card.get("type", "Speed"), 1.0)

    stat_synergy = 1.25 if card.get("type") == preferred else 1.0

    event_bonus = card.get("event_bonus", 0) * EVENT_BONUS_WEIGHT

    skill_score = evaluate_skills(card)

    scenario_bonus = SCENARIO_MULTIPLIER.get(scenario, 1.0)

    total = (
        rarity_score +
        (rarity_score * type_bonus * stat_synergy * 0.3) +
        event_bonus +
        skill_score
    )

    return total * scenario_bonus


# ==========================================================
# DUPLICATE SKILL PENALTY
# ==========================================================

def skill_overlap_penalty(deck):
    seen = set()
    penalty = 0

    for card in deck:
        for skill in card.get("skills", []):
            if skill in seen:
                penalty += 20
            seen.add(skill)

    return penalty


# ==========================================================
# DECK SCORING
# ==========================================================

def score_deck(deck, horse, scenario):

    base_score = sum(score_card(c, horse, scenario) for c in deck)

    overlap_pen = skill_overlap_penalty(deck)

    # Encourage stat diversity
    type_counts = {}
    for c in deck:
        t = c.get("type")
        type_counts[t] = type_counts.get(t, 0) + 1

    diversity_bonus = 0
    if len(type_counts) >= 3:
        diversity_bonus += 50

    # Encourage 2+ preferred stat supports
    preferred = horse.get("preferred_stat", "Speed")
    preferred_count = type_counts.get(preferred, 0)

    if preferred_count >= 2:
        diversity_bonus += 75

    return base_score + diversity_bonus - overlap_pen


# ==========================================================
# RECOMMENDATION ENGINE
# ==========================================================

def recommend_deck(horse, scenario, cards):

    # Filter non-blacklisted
    available = [
        c for c in cards
        if not c.get("blacklisted")
    ]

    if len(available) < 6:
        return []

    # Pre-score and sort top 30 candidates for combinatorial speed
    scored_cards = sorted(
        available,
        key=lambda c: score_card(c, horse, scenario),
        reverse=True
    )[:30]

    best_score = -math.inf
    best_deck = []

    # Evaluate all 6-card combinations from top 30
    for combo in itertools.combinations(scored_cards, 6):

        deck_score = score_deck(combo, horse, scenario)

        if deck_score > best_score:
            best_score = deck_score
            best_deck = combo

    return list(best_deck)
