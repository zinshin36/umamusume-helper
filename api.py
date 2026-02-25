import requests
import logging
import time

BASE = "https://umapyoi.net/api/v1"

logger = logging.getLogger(__name__)


class UmaAPI:

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    # ================= SAFE REQUEST =================

    def fetch_json(self, url):
        try:
            r = requests.get(url, timeout=20)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            logger.error(f"Request failed: {url} | {e}")
            raise RuntimeError(str(e))

    # ================= HORSES =================

    def fetch_all_horses(self):

        data = self.fetch_json(f"{BASE}/character")

        if not isinstance(data, list):
            raise RuntimeError("Unexpected /character response format")

        horses = []
        total = len(data)

        for idx, entry in enumerate(data):

            # SAFE extraction
            char_id = entry.get("id") or entry.get("chara_id")
            name = entry.get("name_en") or entry.get("name")

            if not char_id:
                continue

            horses.append({
                "id": char_id,
                "name": name if name else f"ID {char_id}",
                "preferred_stat": "Speed"
            })

            if self.progress_callback and idx % 10 == 0:
                percent = 5 + int((idx / total) * 40)
                self.progress_callback(
                    f"Fetching horses {idx}/{total}",
                    percent
                )

        return horses

    # ================= SUPPORTS =================

    def fetch_all_supports(self):

        data = self.fetch_json(f"{BASE}/support")

        if not isinstance(data, list):
            raise RuntimeError("Unexpected /support response format")

        supports = []
        total = len(data)

        for idx, entry in enumerate(data):

            support_id = entry.get("id")

            if not support_id:
                continue

            name = entry.get("title_en") or f"ID {support_id}"

            supports.append({
                "id": support_id,
                "name": name,
                "rarity": "SSR" if support_id < 20000 else "SR",
                "type": "Speed",
                "event_bonus": 0,
                "skills": [],
                "image": f"data/images/support/{support_id}.png",
                "blacklisted": False
            })

            if self.progress_callback and idx % 20 == 0:
                percent = 50 + int((idx / total) * 45)
                self.progress_callback(
                    f"Fetching supports {idx}/{total}",
                    percent
                )

            # Respect rate limit
            time.sleep(0.12)

        return supports
