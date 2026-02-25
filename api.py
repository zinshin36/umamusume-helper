import requests
import logging
import time

BASE = "https://umapyoi.net/api/v1"

logger = logging.getLogger(__name__)

REQUEST_DELAY = 0.12  # stays under 10 req/sec


class UmaAPI:

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    # ================= SAFE REQUEST =================

    def fetch_json(self, url):
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            time.sleep(REQUEST_DELAY)
            return r.json()
        except Exception as e:
            logger.error(f"Request failed: {url} | {e}")
            raise RuntimeError(f"API request failed: {url}")

    # ================= HORSES =================

    def fetch_all_horses(self):

        data = self.fetch_json(f"{BASE}/character")

        if not isinstance(data, list):
            raise RuntimeError("Unexpected /character structure")

        horses = []
        total = len(data)

        for idx, entry in enumerate(data):

            char_id = entry.get("id") or entry.get("chara_id")
            name = entry.get("name_en") or entry.get("name")

            if not char_id:
                continue

            horses.append({
                "id": char_id,
                "name": name if name else f"ID {char_id}",
                "preferred_stat": "Speed"  # phase 3: real stat logic
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

        data = self.fetch_json(f"{BASE}/support")

        if not isinstance(data, list):
            raise RuntimeError("Unexpected /support structure")

        return data

    # ================= FULL SUPPORT DETAIL =================

    def fetch_support_detail(self, support_id):
        return self.fetch_json(f"{BASE}/support/{support_id}")

    # ================= SUPPORTS FULL BUILD =================

    def fetch_all_supports(self):

        support_list = self.fetch_support_list()
        total = len(support_list)

        supports = []

        for idx, entry in enumerate(support_list):

            support_id = entry.get("id")
            if not support_id:
                continue

            detail = self.fetch_support_detail(support_id)

            rarity = detail.get("rarity", "R")

            support_type = detail.get("support_type") or detail.get("type") or "Speed"

            event_bonus = detail.get("event_bonus") or 0

            skills = []
            for skill in detail.get("skills", []):
                name = skill.get("name_en") or skill.get("name")
                if name:
                    skills.append(name)

            name = (
                detail.get("title_en")
                or detail.get("name_en")
                or entry.get("title_en")
                or f"ID {support_id}"
            )

            supports.append({
                "id": support_id,
                "name": name,
                "rarity": rarity,
                "type": support_type,
                "event_bonus": event_bonus,
                "skills": skills,
                "image": f"data/images/support/{support_id}.png",
                "blacklisted": False
            })

            if self.progress_callback and idx % 5 == 0:
                percent = 25 + int((idx / total) * 70)
                self.progress_callback(
                    f"Fetching supports {idx}/{total}",
                    percent
                )

        return supports
