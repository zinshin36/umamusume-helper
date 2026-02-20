import requests
from config import HORSES_API, CARDS_API

def fetch_horses():
    """Fetch all horse versions from global server"""
    try:
        r = requests.get(HORSES_API)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching horses: {e}")
        return []

def fetch_cards():
    """Fetch all support card versions from global server"""
    try:
        r = requests.get(CARDS_API)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"Error fetching cards: {e}")
        return []
