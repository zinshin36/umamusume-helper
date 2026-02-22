import requests
import time
import random
import logging
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

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
            logging.warning("Could not read robots.txt")

    def allowed(self, url):
        return self.robot_parser.can_fetch("*", url)

    def get(self, url):
        if not self.allowed(url):
            logging.warning(f"Blocked by robots.txt: {url}")
            return None

        delay = random.uniform(DELAY_MIN, DELAY_MAX)
        time.sleep(delay)

        response = self.session.get(url, timeout=20)

        if response.status_code in (403, 429):
            logging.error(f"Blocked by server: {response.status_code}")
            return None

        response.raise_for_status()
        return response.text
