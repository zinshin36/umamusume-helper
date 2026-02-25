import random
from collections import defaultdict


RARITY_MULT = {
    "SSR": 1.0,
    "SR": 0.8,
    "R": 0.5
}


class DeckOptimizer:

    def __init__(self, supports, horse, scenario):
        self.supports = [s for s in supports if not s.get("blacklisted", False)]
        self.horse = horse
        self.scenario = scenario

    def score_support(self, support):

        rarity_score = RARITY_MULT.get(support["rarity"], 0.4)

        total_stat_value = 0

        for stat, value in support.get("stat_bonus", {}).items():
            growth = self.horse["growth"].get(stat, 0)
            total_stat_value += value * (1 + growth * 0.01)

        event_bonus = support.get("event_bonus", 0)

        return rarity_score * (total_stat_value + event_bonus)

    def build_best_deck(self):

        if not self.supports:
            return []

        scored = [(s, self.score_support(s)) for s in self.supports]
        scored.sort(key=lambda x: x[1], reverse=True)

        return [s[0] for s in scored[:6]]
