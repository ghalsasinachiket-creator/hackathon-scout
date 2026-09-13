"""
unstop_client.py
Uses the "Unstop API" wrapper on RapidAPI — a real documented REST API,
no headless browser needed for Unstop.

Free tier is capped at 6 requests/month, so this caches the raw response
to disk after the first successful live call and reads from that cache
on every run after.

IMPORTANT: a live call only ever fires if UNSTOP_LIVE_FETCH=1 is set in
the environment. Without it, a missing cache just returns {} instead of
silently spending one of your 6 calls. This means Streamlit reruns,
`python -m clients.unstop_client` test runs, and app restarts are all
100% safe by default.

To spend one deliberate call and populate the cache:
    UNSTOP_LIVE_FETCH=1 python -m clients.unstop_client

Only delete unstop_cache.json when you deliberately want to spend
another one of your remaining requests on fresh data (e.g. right before
your actual submission/demo).
"""
import json
import os
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

# Live calls are opt-in only — see module docstring.
LIVE_FETCH = os.getenv("UNSTOP_LIVE_FETCH") == "1"


def _title_matches(title: str, query: str) -> bool:
    words = query.lower().split()
    title_lower = title.lower()
    return any(re.search(rf'\b{re.escape(w)}\b', title_lower) for w in words)


def _get_raw_data() -> dict:
    """Returns the raw API response, from cache if available, else one
    live call — and only if UNSTOP_LIVE_FETCH=1 is set."""
    if CACHE_FILE.exists():
        print("[unstop_client] using cached response (unstop_cache.json)")
        return json.loads(CACHE_FILE.read_text())

    if not LIVE_FETCH:
        print(
            "[unstop_client] no cache found and UNSTOP_LIVE_FETCH is not set — "
            "skipping live call to avoid spending quota. Run with "
            "UNSTOP_LIVE_FETCH=1 to deliberately spend one of your 6 "
            "monthly requests and populate the cache."
        )
        return {}

    try:
        resp = requests.get(
            f"https://{HOST}/hackathons",
            headers=HEADERS,
            params={"page": 1},
            timeout=10,
        )
        remaining = resp.headers.get("X-RateLimit-Requests-Remaining")
        if remaining is not None:
            print(f"[unstop_client] requests remaining this period: {remaining}")
        resp.raise_for_status()
        data = resp.json()
        CACHE_FILE.write_text(json.dumps(data))
        print("[unstop_client] live request succeeded, cached to unstop_cache.json")
        return data
    except requests.exceptions.RequestException as e:
        body = getattr(e.response, "text", "")
        print(f"[unstop_client] request failed: {e} | body: {body}")
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