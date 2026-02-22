import os
import hashlib

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)


def cache_path(url):
    filename = hashlib.md5(url.encode()).hexdigest() + ".html"
    return os.path.join(CACHE_DIR, filename)


def load_cache(url):
    path = cache_path(url)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


def save_cache(url, content):
    path = cache_path(url)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
