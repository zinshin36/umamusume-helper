import requests
import time
import random
import logging
from urllib.parse import urlparse
from utils.cache import load_cache, save_cache

DELAY_MIN = 2
DELAY_MAX = 3


class SafeCrawler:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })

    def allowed(self, url):
        parsed = urlparse(url)

        # Respect rules you provided
        if "/api/" in parsed.path:
            return False
        if "/admin/" in parsed.path:
            return False

        return True

    def get(self, url):
        if not self.allowed(url):
            logging.warning(f"Blocked by manual robots policy: {url}")
            return None

        cached = load_cache(url)
        if cached:
            return cached

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        try:
            response = self.session.get(url, timeout=20)
        except Exception as e:
            logging.error(f"Request failed: {e}")
            return None

        if response.status_code in (403, 429):
            logging.error(f"Server blocked request: {response.status_code}")
            return None

        if response.status_code != 200:
            return None

        save_cache(url, response.text)
        return response.text
