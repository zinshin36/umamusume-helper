import requests
import logging
import time
import os

BASE = "https://umapyoi.net/api/v1"
IMAGE_BASE = "https://umapyoi.net"

REQUEST_DELAY = 0.12

logger = logging.getLogger(__name__)


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

        data = self.fetch_json(f"{BASE}/character")

        horses = []
        total = len(data)

        for idx, entry in enumerate(data):

            char_id = entry.get("id") or entry.get("chara_id")

            name = (
                entry.get("name_en")
                or entry.get("name")
                or entry.get("title_en")
            )

            if not char_id or not name:
                continue

            horses.append({
                "id": char_id,
                "name": name,
                "preferred_stat": "Speed"
            })

            if self.progress_callback and idx % 10 == 0:
                percent = 5 + int((idx / total) * 20)
                self.progress_callback(
                    f"Fetching horses {idx}/{total}",
                    percent
                )

        return horses

    # ================= SUPPORT LIST =================

    def fetch_support_list(self):
        return self.fetch_json(f"{BASE}/support")

    # ================= SUPPORT DETAIL =================

    def fetch_support_detail(self, support_id):
        return self.fetch_json(f"{BASE}/support/{support_id}")

    # ================= FULL SUPPORT BUILD =================

    def fetch_all_supports(self):

        support_list = self.fetch_support_list()
        total = len(support_list)

        supports = []

        os.makedirs("data/images/support", exist_ok=True)

        for idx, entry in enumerate(support_list):

            support_id = entry.get("id")
            if not support_id:
                continue

            detail = self.fetch_support_detail(support_id)

            rarity = detail.get("rarity", "R")
            support_type = detail.get("support_type", "Speed")
            event_bonus = detail.get("event_bonus", 0)

            skills = []
            for skill in detail.get("skills", []):
                name = skill.get("name_en") or skill.get("name")
                if name:
                    skills.append(name)

            name = (
                detail.get("title_en")
                or detail.get("name_en")
                or entry.get("title_en")
            )

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
                "skills": skills,
                "image": image_path,
                "blacklisted": False
            })

            if self.progress_callback and idx % 5 == 0:
                percent = 30 + int((idx / total) * 65)
                self.progress_callback(
                    f"Fetching supports {idx}/{total}",
                    percent
                )

        return supports
