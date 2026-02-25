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

    # ================= PAGINATION HANDLER =================

    def fetch_paginated(self, endpoint, start_percent, end_percent):

        url = f"{BASE}/{endpoint}"
        all_results = []
        page_count = 0

        while url:

            data = self.fetch_json(url)

            results = data.get("results", [])
            all_results.extend(results)

            page_count += 1

            if self.progress_callback:
                percent = start_percent + int(
                    (len(all_results) / data.get("count", 1)) * (end_percent - start_percent)
                )
                self.progress_callback(
                    f"Fetching {endpoint} page {page_count} ({len(all_results)}/{data.get('count')})",
                    percent
                )

            url = data.get("next")

            # respect rate limit (10 req/sec)
            time.sleep(0.12)

        return all_results

    # ================= HORSES =================

    def fetch_all_horses(self):

        horses_raw = self.fetch_paginated("character", 5, 45)

        horses = []

        for h in horses_raw:
            horses.append({
                "id": h["id"],
                "name": h.get("name_en") or h.get("name"),
                "preferred_stat": "Speed"  # will improve later
            })

        return horses

    # ================= SUPPORTS =================

    def fetch_all_supports(self):

        supports_raw = self.fetch_paginated("support", 50, 95)

        supports = []

        for s in supports_raw:

            supports.append({
                "id": s["id"],
                "name": s.get("name_en") or s.get("name"),
                "rarity": s.get("rarity", "R"),
                "type": s.get("support_type", "Speed"),
                "event_bonus": s.get("event_bonus", 0),
                "skills": [
                    sk.get("name_en")
                    for sk in s.get("skills", [])
                    if sk.get("name_en")
                ],
                "image": f"data/images/support/{s['id']}.png",
                "blacklisted": False
            })

        return supports
