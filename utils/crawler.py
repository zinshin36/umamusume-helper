import requests
import time
import random
import logging
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from utils.cache import load_cache, save_cache

DELAY_MIN = 2
DELAY_MAX = 5


class SafeCrawler:
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(urljoin(base_url, "/robots.txt"))
        try:
            self.robot_parser.read()
        except Exception:
            logging.warning("robots.txt could not be read")

    def allowed(self, url):
        return self.robot_parser.can_fetch("*", url)

    def get(self, url):
        cached = load_cache(url)
        if cached:
            return cached

        if not self.allowed(url):
            logging.warning(f"Blocked by robots.txt: {url}")
            return None

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

        response = self.session.get(url, timeout=20)

        if response.status_code in (403, 429):
            logging.error(f"Server blocked request: {response.status_code}")
            return None

        response.raise_for_status()

        save_cache(url, response.text)
        return response.text
