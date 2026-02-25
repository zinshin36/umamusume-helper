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
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {url} | {e}")
            raise RuntimeError(f"API request failed: {url}")

    # ================= HORSES =================

    def fetch_all_horses(self):

        if self.progress_callback:
            self.progress_callback("Fetching horses...", 5)

        # IMPORTANT: this endpoint is NOT paginated
        data = self.fetch_json(f"{BASE}/character")

        horses = []

        for idx, h in enumerate(data):

            horses.append({
                "id": h["id"],
                "name": h.get("name_en") or h.get("name") or f"ID {h['id']}",
                "preferred_stat": "Speed"
            })

            if self.progress_callback and idx % 10 == 0:
                percent = 5 + int((idx / len(data)) * 40)
                self.progress_callback(f"Fetching horses... {idx}/{len(data)}", percent)

        return horses

    # ================= SUPPORTS =================

    def fetch_all_supports(self):

        if self.progress_callback:
            self.progress_callback("Fetching supports...", 50)

        # IMPORTANT: also NOT paginated
        data = self.fetch_json(f"{BASE}/support")

        supports = []

        for idx, s in enumerate(data):

            supports.append({
                "id": s["id"],
                "name": s.get("name_en") or s.get("name") or f"ID {s['id']}",
                "rarity": s.get("rarity", "R"),
                "type": s.get("support_type", "Speed"),
                "event_bonus": s.get("event_bonus", 0),
                "skills": [
                    sk.get("name_en") for sk in s.get("skills", [])
                    if sk.get("name_en")
                ],
                "image": f"data/images/support/{s['id']}.png",
                "blacklisted": False
            })

            if self.progress_callback and idx % 20 == 0:
                percent = 50 + int((idx / len(data)) * 45)
                self.progress_callback(
                    f"Fetching supports... {idx}/{len(data)}",
                    percent
                )

        return supports
