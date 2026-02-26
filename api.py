import requests
import logging
import time
import os

BASE = "https://umapyoi.net/api/v1"

REQUEST_DELAY = 0.15
logger = logging.getLogger(__name__)


class UmaAPI:

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    # ---------------- REQUEST ----------------

    def fetch_json(self, url):
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return r.json()

    # ---------------- IMAGE ----------------

    def download_image(self, url, save_path):

        if not url:
            return

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        if os.path.exists(save_path):
            return

        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            logger.error(f"Image download failed: {url} | {e}")

    # ---------------- HORSES ----------------

    def fetch_all_horses(self):

        horses_index = self.fetch_json(f"{BASE}/character")

        horses = []
        total = len(horses_index)

        for i, entry in enumerate(horses_index):

            game_id = entry.get("game_id")
            if not game_id:
                continue

            detail = self.fetch_json(f"{BASE}/character/{game_id}")

            name = detail.get("name_en") or detail.get("name")

            # REAL growth location (from API docs)
            growth_rate = detail.get("proper", {}).get("growth_rate", {})

            growth = {
                "Speed": growth_rate.get("speed", 0),
                "Stamina": growth_rate.get("stamina", 0),
                "Power": growth_rate.get("power", 0),
                "Guts": growth_rate.get("guts", 0),
                "Wisdom": growth_rate.get("wiz", 0)
            }

            image_url = detail.get("image")

            image_path = f"data/images/horse/{game_id}.png"
            self.download_image(image_url, image_path)

            horses.append({
                "id": game_id,
                "name": name,
                "growth": growth,
                "image": image_path
            })

            if self.progress_callback and i % 3 == 0:
                percent = 5 + int((i / max(total, 1)) * 30)
                self.progress_callback(f"Fetching horses {i}/{total}", percent)

        return horses

    # ---------------- SUPPORTS ----------------

    def fetch_all_supports(self):

        supports_index = self.fetch_json(f"{BASE}/support")

        supports = []
        total = len(supports_index)

        for i, entry in enumerate(supports_index):

            support_id = entry.get("id")
            if not support_id:
                continue

            detail = self.fetch_json(f"{BASE}/support/{support_id}")

            name = detail.get("title_en") or detail.get("name_en")

            rarity_raw = detail.get("rarity", 1)
            rarity = {3: "SSR", 2: "SR", 1: "R"}.get(rarity_raw, "R")

            support_type = detail.get("type", "Speed")

            # REAL stat bonuses from "effects"
            effects = detail.get("effects", [])

            stat_bonus = {
                "Speed": 0,
                "Stamina": 0,
                "Power": 0,
                "Guts": 0,
                "Wisdom": 0
            }

            for effect in effects:
                effect_type = effect.get("type")
                value = effect.get("value", 0)

                if effect_type == "speed_bonus":
                    stat_bonus["Speed"] += value
                elif effect_type == "stamina_bonus":
                    stat_bonus["Stamina"] += value
                elif effect_type == "power_bonus":
                    stat_bonus["Power"] += value
                elif effect_type == "guts_bonus":
                    stat_bonus["Guts"] += value
                elif effect_type == "wiz_bonus":
                    stat_bonus["Wisdom"] += value

            event_bonus = detail.get("event_bonus", 0)

            skills = []
            for skill in detail.get("skills", []):
                skill_name = skill.get("name_en") or skill.get("name")
                if skill_name:
                    skills.append(skill_name)

            image_url = detail.get("image")
            image_path = f"data/images/support/{support_id}.png"

            self.download_image(image_url, image_path)

            supports.append({
                "id": support_id,
                "name": name,
                "rarity": rarity,
                "type": support_type,
                "event_bonus": event_bonus,
                "stat_bonus": stat_bonus,
                "skills": skills,
                "image": image_path,
                "blacklisted": False
            })

            if self.progress_callback and i % 3 == 0:
                percent = 40 + int((i / max(total, 1)) * 55)
                self.progress_callback(f"Fetching supports {i}/{total}", percent)

        return supports
