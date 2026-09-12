"""
unstop_client.py
Uses the "Unstop API" wrapper on RapidAPI — a real documented REST API,
no headless browser needed for Unstop.

Free tier is capped at 6 requests/month, so this caches the raw response
to disk after the first successful live call and reads from that cache
on every run after — only delete unstop_cache.json when you deliberately
want to spend one of your remaining requests on fresh data (e.g. right
before your actual submission/demo).
"""
import json
import re
import requests
from pathlib import Path
from config import get_secret
from schema import Opportunity

RAPIDAPI_KEY = get_secret("RAPIDAPI_KEY")
HOST = "unstop-api.p.rapidapi.com"
HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": HOST,
}

CACHE_FILE = Path(__file__).parent / "unstop_cache.json"


def _title_matches(title: str, query: str) -> bool:
    words = query.lower().split()
    title_lower = title.lower()
    return any(re.search(rf'\b{re.escape(w)}\b', title_lower) for w in words)


def _get_raw_data() -> dict:
    """Returns the raw API response, from cache if available, else one live call."""
    if CACHE_FILE.exists():
        print("[unstop_client] using cached response (unstop_cache.json)")
        return json.loads(CACHE_FILE.read_text())

    try:
        resp = requests.get(
            f"https://{HOST}/hackathons",
            headers=HEADERS,
            params={"page": 1},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        CACHE_FILE.write_text(json.dumps(data))
        print("[unstop_client] live request succeeded, cached to unstop_cache.json")
        return data
    except requests.exceptions.RequestException as e:
        print(f"[unstop_client] request failed: {e}")
        return {}


def search_unstop_hackathons(query: str, limit: int = 10) -> list[Opportunity]:
    data = _get_raw_data()
    all_results = data.get("results", [])

    matches = [item for item in all_results if _title_matches(item.get("title", ""), query)]

    output = []
    for item in matches[:limit]:
        raw_url = item.get("url") or item.get("public_url")
        if raw_url and not raw_url.startswith("http"):
            raw_url = f"https://unstop.com/{raw_url}"

        output.append({
            "title": item.get("title"),
            "platform": "unstop",
            "url": raw_url,
            "prize_money": item.get("overall_prizes"),
            "deadline": item.get("end_date"),
            "location": item.get("region"),
            "team_size": None,
            "registration_status": "open" if item.get("regn_open") else "closed",
            "tags": [],
            "source_query": query,
        })
    return output


if __name__ == "__main__":
    for r in search_unstop_hackathons("AI robotics"):
        print(r["title"], "-", r["url"])
