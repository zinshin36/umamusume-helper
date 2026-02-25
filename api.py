import requests
import time

BASE = "https://umapyoi.net/api/v1"

class UmaAPI:

    def __init__(self, progress_callback=None):
        self.progress_callback = progress_callback

    def rate_limit(self):
        time.sleep(0.12)  # stays under 10 req/sec

    def fetch_json(self, url):
        self.rate_limit()
        r = requests.get(url)
        r.raise_for_status()
        return r.json()

    def fetch_all_horses(self):

        horses = []
        page = 1

        while True:
            data = self.fetch_json(f"{BASE}/character?page={page}")
            results = data.get("results", [])
            if not results:
                break

            for h in results:
                horses.append({
                    "id": h["id"],
                    "name": h.get("name_en") or h.get("name"),
                    "preferred_stat": "Speed"  # placeholder until deeper stat logic added
                })

            if self.progress_callback:
                self.progress_callback(f"Fetched horses page {page}", page)

            page += 1

        return horses

    def fetch_all_supports(self):

        supports = []
        page = 1

        while True:
            data = self.fetch_json(f"{BASE}/support?page={page}")
            results = data.get("results", [])
            if not results:
                break

            for s in results:
                supports.append({
                    "id": s["id"],
                    "name": s.get("name_en") or s.get("name") or "Unknown",
                    "rarity": s.get("rarity", "R"),
                    "type": s.get("support_type", "Speed"),
                    "event_bonus": s.get("event_bonus", 0),
                    "skills": [sk["name_en"] for sk in s.get("skills", []) if "name_en" in sk],
                    "image": f"data/images/support/{s['id']}.png",
                    "blacklisted": False
                })

            if self.progress_callback:
                self.progress_callback(f"Fetched supports page {page}", page)

            page += 1

        return supports
