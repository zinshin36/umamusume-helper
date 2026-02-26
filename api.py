import requests
import logging
import time
import os

BASE = "https://umapyoi.net/api/v1"
CDN_BASE = "https://umapyoi.net"

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

    # ================= IMAGE DOWNLOAD =================

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

            # Growth stats are inside "status"
            status = detail.get("status", {})

            growth = {
                "Speed": status.get("speed_growth", 0),
                "Stamina": status.get("stamina_growth", 0),
                "Power": status.get("power_growth", 0),
                "Guts": status.get("guts_growth", 0),
                "Wisdom": status.get("wisdom_growth", 0)
            }

            # Optional horse image
            image_path = f"data/images/horse/{game_id}.png"
            image_url = f"{CDN_BASE}/static/characters/{game_id}.png"
            self.download_image(image_url, image_path)

            horses.append({
                "id": game_id,
                "name": name,
                "growth": growth,
                "image": image_path
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

            rarity = RARITY_MAP.get(detail.get("rarity", 1), "R")
            support_type = detail.get("type", "Speed")

            # Stat bonuses inside training_bonus
            training_bonus = detail.get("training_bonus", {})

            stat_bonus = {
                "Speed": training_bonus.get("speed", 0),
                "Stamina": training_bonus.get("stamina", 0),
                "Power": training_bonus.get("power", 0),
                "Guts": training_bonus.get("guts", 0),
                "Wisdom": training_bonus.get("wisdom", 0)
            }

            event_bonus = detail.get("event_bonus", 0)

            skills = []
            for skill in detail.get("skills", []):
                name = skill.get("name_en") or skill.get("name")
                if name:
                    skills.append(name)

            name = detail.get("title_en") or detail.get("name_en")

            # Support card image pattern
            image_url = f"{CDN_BASE}/static/supports/{support_id}.png"
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
