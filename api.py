import requests
import logging
import time
import os

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
            return

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        try:
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            logger.error(f"Image download failed: {url} | {e}")

    # ================= HORSES (GAMEPLAY DATA) =================

    def fetch_all_horses(self):

        horse_list = self.fetch_json(f"{BASE}/uma")
        horses = []

        for i, horse in enumerate(horse_list):

            game_id = horse.get("id")
            name = horse.get("name_en")

            growth = {
                "Speed": horse.get("speed_growth", 0),
                "Stamina": horse.get("stamina_growth", 0),
                "Power": horse.get("power_growth", 0),
                "Guts": horse.get("guts_growth", 0),
                "Wisdom": horse.get("wiz_growth", 0)
            }

            running_style = horse.get("strategy")

            image_url = horse.get("image")
            image_path = f"data/images/horse/{game_id}.png"

            self.download_image(image_url, image_path)

            horses.append({
                "id": game_id,
                "name": name,
                "growth": growth,
                "strategy": running_style,
                "image": image_path
            })

        return horses

    # ================= SUPPORT CARDS (GAMEPLAY DATA) =================

    def fetch_all_supports(self):

        support_list = self.fetch_json(f"{BASE}/supportcard")
        supports = []

        for support in support_list:

            support_id = support.get("id")
            name = support.get("name_en")

            stat_bonus = {
                "Speed": support.get("speed_bonus", 0),
                "Stamina": support.get("stamina_bonus", 0),
                "Power": support.get("power_bonus", 0),
                "Guts": support.get("guts_bonus", 0),
                "Wisdom": support.get("wiz_bonus", 0)
            }

            rarity = support.get("rarity_string")
            support_type = support.get("type")

            image_url = support.get("image")
            image_path = f"data/images/support/{support_id}.png"

            self.download_image(image_url, image_path)

            supports.append({
                "id": support_id,
                "name": name,
                "rarity": rarity,
                "type": support_type,
                "stat_bonus": stat_bonus,
                "image": image_path,
                "blacklisted": False
            })

        return supports
