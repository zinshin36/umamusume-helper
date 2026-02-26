import requests
import logging
import time
import os

BASE = "https://umapyoi.net/api/v1"
IMAGE_BASE = "https://umapyoi.net"

REQUEST_DELAY = 0.12

logger = logging.getLogger(__name__)

RARITY_MAP = {
    3: "SSR",
    2: "SR",
    1: "R"
}


class UmaAPI:

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    # ================= SAFE REQUEST =================

    def fetch_json(self, url):
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        time.sleep(REQUEST_DELAY)
        return r.json()

    # ================= IMAGE =================

    def download_image(self, url, save_path):

        if not url:
            return

        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        if os.path.exists(save_path):
            return

        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            with open(save_path, "wb") as f:
                f.write(r.content)
        except Exception as e:
            logger.error(f"Image download failed: {url} | {e}")

    # ================= HORSES =================

    def fetch_all_horses(self):

        id_list = self.fetch_json(f"{BASE}/character")

        horses = []
        total = len(id_list)

        for idx, entry in enumerate(id_list):

            game_id = entry.get("game_id")
            if not game_id:
                continue

            detail = self.fetch_json(f"{BASE}/character/{game_id}")

            name = detail.get("name_en") or detail.get("name")

            if not name:
                continue

            horses.append({
                "id": game_id,
                "name": name,
                "growth": {
                    "Speed": detail.get("speed_growth", 0),
                    "Stamina": detail.get("stamina_growth", 0),
                    "Power": detail.get("power_growth", 0),
                    "Guts": detail.get("guts_growth", 0),
                    "Wisdom": detail.get("wisdom_growth", 0)
                }
            })

            if self.progress_callback and idx % 3 == 0:
                percent = 5 + int((idx / max(total, 1)) * 25)
                self.progress_callback(
                    f"Fetching horses {idx}/{total}",
                    percent
                )

        return horses

    # ================= SUPPORTS =================

    def fetch_all_supports(self):

        support_list = self.fetch_json(f"{BASE}/support")
        total = len(support_list)

        supports = []

        for idx, entry in enumerate(support_list):

            support_id = entry.get("id")
            if not support_id:
                continue

            detail = self.fetch_json(f"{BASE}/support/{support_id}")

            rarity_num = detail.get("rarity", 1)
            rarity = RARITY_MAP.get(rarity_num, "R")

            support_type = detail.get("support_type", "Speed")

            stat_bonus = {
                "Speed": detail.get("speed_bonus", 0),
                "Stamina": detail.get("stamina_bonus", 0),
                "Power": detail.get("power_bonus", 0),
                "Guts": detail.get("guts_bonus", 0),
                "Wisdom": detail.get("wisdom_bonus", 0)
            }

            event_bonus = detail.get("event_bonus", 0)

            skills = []
            for skill in detail.get("skills", []):
                name = skill.get("name_en") or skill.get("name")
                if name:
                    skills.append(name)

            name = detail.get("title_en") or detail.get("name_en")

            image_url = detail.get("image")
            if image_url:
                image_url = IMAGE_BASE + image_url

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

            if self.progress_callback and idx % 3 == 0:
                percent = 35 + int((idx / max(total, 1)) * 60)
                self.progress_callback(
                    f"Fetching supports {idx}/{total}",
                    percent
                )

        return supports
