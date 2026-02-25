import requests
import time
import logging

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
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {url} | {e}")
            raise RuntimeError(f"Request failed: {url}")

    # ================= HORSES =================

    def fetch_all_horses(self):

        if self.progress_callback:
            self.progress_callback("Fetching horses...", 5)

        data = self.fetch_json(f"{BASE}/character")

        if not isinstance(data, list):
            raise RuntimeError("Unexpected /character structure")

        horses = []

        total = len(data)

        for idx, h in enumerate(data):

            horses.append({
                "id": h["id"],
                "name": h.get("name_en") or h.get("name") or f"ID {h['id']}",
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

        if self.progress_callback:
            self.progress_callback("Fetching supports...", 50)

        data = self.fetch_json(f"{BASE}/support")

        if not isinstance(data, list):
            raise RuntimeError("Unexpected /support structure")

        supports = []
        total = len(data)

        for idx, s in enumerate(data):

            supports.append({
                "id": s["id"],
                "name": s.get("title_en") or f"ID {s['id']}",
                "rarity": "SSR" if s["id"] < 20000 else "SR",  # simple fallback
                "type": "Speed",  # placeholder until deeper endpoint used
                "event_bonus": 0,
                "skills": [],
                "image": f"data/images/support/{s['id']}.png",
                "blacklisted": False
            })

            if self.progress_callback and idx % 20 == 0:
                percent = 50 + int((idx / total) * 45)
                self.progress_callback(
                    f"Fetching supports {idx}/{total}",
                    percent
                )

        return supports
