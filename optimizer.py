import random
from collections import defaultdict

RARITY_WEIGHT = {
    "SSR": 1.0,
    "SR": 0.75,
    "R": 0.45
}

SCENARIO_STAT_CAPS = {
    "Aoharu": {"Speed": 1200, "Stamina": 1200, "Power": 1200, "Guts": 1200, "Wisdom": 1200},
    "URA": {"Speed": 1200, "Stamina": 1200, "Power": 1200, "Guts": 1200, "Wisdom": 1200},
    "Grand Live": {"Speed": 1600, "Stamina": 1600, "Power": 1600, "Guts": 1600, "Wisdom": 1600},
}

class DeckOptimizer:

    def __init__(self, supports, horse, scenario, simulation_mode=True):
        self.supports = [s for s in supports if not s.get("blacklisted", False)]
        self.horse = horse
        self.scenario = scenario
        self.simulation_mode = simulation_mode
        self.stat_caps = SCENARIO_STAT_CAPS.get(scenario, SCENARIO_STAT_CAPS["URA"])

    def score_support(self, support):

        rarity_score = RARITY_WEIGHT.get(support["rarity"], 0.3)

        preferred_stat = self.horse.get("preferred_stat", "Speed")
        type_match = 1.3 if support["type"] == preferred_stat else 1.0

        event_bonus_score = 1 + (support.get("event_bonus", 0) * 0.05)

        skill_score = len(support.get("skills", [])) * 0.03

        total_score = rarity_score * type_match * event_bonus_score + skill_score

        return total_score

    def avoid_duplicate_skills(self, deck):
        seen = set()
        filtered = []
        for s in deck:
            unique_skills = [sk for sk in s["skills"] if sk not in seen]
            if unique_skills:
                seen.update(unique_skills)
                filtered.append(s)
        return filtered

    def simulate_training(self, deck):

        stat_gain = defaultdict(int)
        preferred_stat = self.horse.get("preferred_stat", "Speed")

        for s in deck:
            base = 100
            rarity_multiplier = RARITY_WEIGHT.get(s["rarity"], 0.4)
            stat_gain[s["type"]] += int(base * rarity_multiplier)

        if preferred_stat in stat_gain:
            stat_gain[preferred_stat] = int(stat_gain[preferred_stat] * 1.2)

        total_score = 0
        for stat, value in stat_gain.items():
            cap = self.stat_caps.get(stat, 1200)
            total_score += min(value, cap)

        return total_score

    def build_best_deck(self):

        scored = [(s, self.score_support(s)) for s in self.supports]
        scored.sort(key=lambda x: x[1], reverse=True)

        if not self.simulation_mode:
            return [s[0] for s in scored[:6]]

        best_score = 0
        best_deck = []

        top_pool = [s[0] for s in scored[:18]]

        for _ in range(3000):
            candidate = random.sample(top_pool, 6)
            candidate = self.avoid_duplicate_skills(candidate)
            if len(candidate) < 6:
                continue

            score = self.simulate_training(candidate)
            if score > best_score:
                best_score = score
                best_deck = candidate

        return best_deck
