import random


class DeckOptimizer:

    def __init__(self):
        pass

    def score_support(self, horse, support):

        score = 0

        growth = horse.get("growth", {})
        support_bonus = support.get("stat_bonus", {})

        # Score based on matching growth
        for stat in ["Speed", "Stamina", "Power", "Guts", "Wisdom"]:
            growth_value = growth.get(stat, 0)
            bonus_value = support_bonus.get(stat, 0)

            score += growth_value * bonus_value

        # Slight bonus for matching type to highest growth stat
        highest_growth_stat = max(growth, key=growth.get)
        if support.get("type") == highest_growth_stat:
            score += 50

        # Small rarity bonus
        rarity_bonus = {
            "SSR": 100,
            "SR": 50,
            "R": 10
        }
        score += rarity_bonus.get(support.get("rarity"), 0)

        return score

    def optimize(self, horse, supports):

        if not supports:
            return []

        scored = []

        for support in supports:
            if support.get("blacklisted"):
                continue

            score = self.score_support(horse, support)
            scored.append((score, support))

        scored.sort(key=lambda x: x[0], reverse=True)

        # Return top 6 cards
        best = [s[1] for s in scored[:6]]

        return best
