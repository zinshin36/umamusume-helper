import random
from collections import defaultdict


RARITY_WEIGHT = {
    "SSR": 1.0,
    "SR": 0.75,
    "R": 0.45
}

TYPE_WEIGHT = {
    "Speed": 1.2,
    "Stamina": 1.1,
    "Power": 1.1,
    "Guts": 1.0,
    "Wisdom": 1.1
}


class DeckOptimizer:

    def __init__(self, supports, horse, scenario, simulation_mode=True):
        self.supports = [s for s in supports if not s.get("blacklisted", False)]
        self.horse = horse
        self.scenario = scenario
        self.simulation_mode = simulation_mode

    # ================= SCORING =================

    def score_support(self, support):

        rarity_score = RARITY_WEIGHT.get(support.get("rarity"), 0.4)

        preferred = self.horse.get("preferred_stat", "Speed")

        type_bonus = 1.3 if support.get("type") == preferred else 1.0

        event_bonus = 1 + (support.get("event_bonus", 0) * 0.02)

        skill_bonus = len(support.get("skills", [])) * 0.05

        type_weight = TYPE_WEIGHT.get(support.get("type"), 1.0)

        return rarity_score * type_bonus * event_bonus * type_weight + skill_bonus

    # ================= SKILL DEDUP =================

    def avoid_duplicate_skills(self, deck):
        seen = set()
        filtered = []
        for s in deck:
            unique = [sk for sk in s.get("skills", []) if sk not in seen]
            if unique:
                seen.update(unique)
                filtered.append(s)
        return filtered

    # ================= SIMULATION =================

    def simulate_training(self, deck):

        stat_gain = defaultdict(int)

        for s in deck:
            base = 100
            rarity_mult = RARITY_WEIGHT.get(s.get("rarity"), 0.4)
            stat_gain[s.get("type")] += int(base * rarity_mult)

        preferred = self.horse.get("preferred_stat", "Speed")
        if preferred in stat_gain:
            stat_gain[preferred] = int(stat_gain[preferred] * 1.2)

        return sum(stat_gain.values())

    # ================= MAIN BUILDER =================

    def build_best_deck(self):

        if not self.supports:
            return []

        scored = [(s, self.score_support(s)) for s in self.supports]
        scored.sort(key=lambda x: x[1], reverse=True)

        if not self.simulation_mode:
            return [s[0] for s in scored[:6]]

        top_pool = [s[0] for s in scored[:20]]

        best_score = 0
        best_deck = []

        for _ in range(5000):
            candidate = random.sample(top_pool, 6)
            candidate = self.avoid_duplicate_skills(candidate)

            if len(candidate) < 6:
                continue

            score = self.simulate_training(candidate)

            if score > best_score:
                best_score = score
                best_deck = candidate

        return best_deck
