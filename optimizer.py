import random
from collections import defaultdict

STAT_CAPS = {
    "URA": 1200,
    "Aoharu": 1200,
    "Grand Live": 1200
}

RARITY_MULT = {
    "SSR": 1.0,
    "SR": 0.75,
    "R": 0.45
}


class DeckOptimizer:

    def __init__(self, supports, horse, scenario):
        self.supports = [s for s in supports if not s.get("blacklisted", False)]
        self.horse = horse
        self.scenario = scenario

    def score_support(self, support):

        rarity = RARITY_MULT.get(support["rarity"], 0.4)

        preferred = self.horse.get("preferred_stat", "Speed")

        type_bonus = 1.3 if support["type"] == preferred else 1.0

        skill_bonus = len(support.get("skills", [])) * 0.05

        return rarity * type_bonus + skill_bonus

    def simulate_training(self, deck):

        stats = defaultdict(int)

        for s in deck:
            base = 120
            mult = RARITY_MULT.get(s["rarity"], 0.4)
            stats[s["type"]] += int(base * mult)

        cap = STAT_CAPS.get(self.scenario, 1200)

        for stat in stats:
            stats[stat] = min(stats[stat], cap)

        return sum(stats.values())

    def build_best_deck(self):

        scored = [(s, self.score_support(s)) for s in self.supports]
        scored.sort(key=lambda x: x[1], reverse=True)

        pool = [s[0] for s in scored[:20]]

        best_score = 0
        best = []

        for _ in range(3000):
            candidate = random.sample(pool, 6)
            score = self.simulate_training(candidate)

            if score > best_score:
                best_score = score
                best = candidate

        return best
