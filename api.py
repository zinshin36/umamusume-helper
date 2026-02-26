import requests
import logging
import time
import os
import json

BASE = "https://umapyoi.net/api/v1"
REQUEST_DELAY = 0.2

logger = logging.getLogger(__name__)


class UmaAPI:

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def fetch_json(self, url):
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return r.json()

    def download_image(self, url, save_path):
        if not url:
            logger.error(f"No image URL provided for {save_path}")
            return

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            logger.error(f"Image download failed: {url} | {e}")

    # ================= HORSES =================

    def fetch_all_horses(self):

        horses_index = self.fetch_json(f"{BASE}/character")
        horses = []

        for i, entry in enumerate(horses_index):

            game_id = entry.get("game_id")
            if not game_id:
                continue

            detail = self.fetch_json(f"{BASE}/character/{game_id}")

            # Save first response for debugging
            if i == 0:
                with open("api_character_debug.json", "w", encoding="utf-8") as f:
                    json.dump(detail, f, indent=2)

            name = detail.get("name_en") or detail.get("name")

            # Inspect available keys
            logger.info(f"Character keys: {list(detail.keys())}")

            growth = {
                "Speed": 0,
                "Stamina": 0,
                "Power": 0,
                "Guts": 0,
                "Wisdom": 0
            }

            # Growth sometimes under "status"
            status = detail.get("status", {})
            if status:
                growth["Speed"] = status.get("speed_growth", 0)
                growth["Stamina"] = status.get("stamina_growth", 0)
                growth["Power"] = status.get("power_growth", 0)
                growth["Guts"] = status.get("guts_growth", 0)
                growth["Wisdom"] = status.get("wiz_growth", 0)

            image_url = detail.get("image")
            image_path = f"data/images/horse/{game_id}.png"
            self.download_image(image_url, image_path)

            horses.append({
                "id": game_id,
                "name": name,
                "growth": growth,
                "image": image_path
            })

        return horses

    # ================= SUPPORTS =================

    def fetch_all_supports(self):

        supports_index = self.fetch_json(f"{BASE}/support")
        supports = []

        for i, entry in enumerate(supports_index):

            support_id = entry.get("id")
            if not support_id:
                continue

            detail = self.fetch_json(f"{BASE}/support/{support_id}")

            if i == 0:
                with open("api_support_debug.json", "w", encoding="utf-8") as f:
                    json.dump(detail, f, indent=2)

            logger.info(f"Support keys: {list(detail.keys())}")

            name = detail.get("title_en") or detail.get("name_en")

            rarity_map = {3: "SSR", 2: "SR", 1: "R"}
            rarity = rarity_map.get(detail.get("rarity"), "R")

            support_type = detail.get("type", "Speed")

            stat_bonus = {
                "Speed": 0,
                "Stamina": 0,
                "Power": 0,
                "Guts": 0,
                "Wisdom": 0
            }

            # Effects array contains bonuses
            effects = detail.get("effects", [])
            for effect in effects:
                effect_type = effect.get("type")
                value = effect.get("value", 0)

                if effect_type == "speed":
                    stat_bonus["Speed"] += value
                elif effect_type == "stamina":
                    stat_bonus["Stamina"] += value
                elif effect_type == "power":
                    stat_bonus["Power"] += value
                elif effect_type == "guts":
                    stat_bonus["Guts"] += value
                elif effect_type == "wiz":
                    stat_bonus["Wisdom"] += value

            event_bonus = detail.get("event_bonus", 0)

            skills = []
            for skill in detail.get("skills", []):
                skills.append(skill.get("name_en") or skill.get("name"))

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

        return supports
