import requests
import logging
import time
import os

BASE = "https://umapyoi.net/api/v1"
REQUEST_DELAY = 0.2

logger = logging.getLogger(__name__)


class UmaAPI:

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

        characters = self.fetch_json(f"{BASE}/character")
        horses = []

        for char in characters:

            game_id = char.get("game_id")
            name = char.get("name_en")

            # fetch gameplay stats
            stats = self.fetch_json(f"{BASE}/character/{game_id}/stats")

            growth = {
                "Speed": stats.get("speed_growth", 0),
                "Stamina": stats.get("stamina_growth", 0),
                "Power": stats.get("power_growth", 0),
                "Guts": stats.get("guts_growth", 0),
                "Wisdom": stats.get("wiz_growth", 0)
            }

            strategy = stats.get("strategy", "Unknown")

            image_url = char.get("detail_img_pc") or char.get("thumb_img")
            image_path = f"data/images/horse/{game_id}.png"

            self.download_image(image_url, image_path)

            horses.append({
                "id": game_id,
                "name": name,
                "growth": growth,
                "strategy": strategy,
                "image": image_path
            })

        return horses

    # ================= SUPPORTS =================

    def fetch_all_supports(self):

        support_list = self.fetch_json(f"{BASE}/support")
        supports = []

        for support in support_list:

            support_id = support.get("id")
            name = support.get("title_en")
            rarity = support.get("rarity_string")
            support_type = support.get("type")

            # fetch gameplay stats
            stats = self.fetch_json(f"{BASE}/support/{support_id}/stats")

            stat_bonus = {
                "Speed": stats.get("speed_bonus", 0),
                "Stamina": stats.get("stamina_bonus", 0),
                "Power": stats.get("power_bonus", 0),
                "Guts": stats.get("guts_bonus", 0),
                "Wisdom": stats.get("wiz_bonus", 0)
            }

            image_url = stats.get("image") or support.get("type_icon_url")
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
