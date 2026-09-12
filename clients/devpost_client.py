"""
devpost_client.py
Lightweight client for interacting with the Devpost API.
No API key needed.
"""
import re
import requests

BASE_URL = "https://devpost.com/api/hackathons"


def _strip_html(text):
    """Strip HTML tags from a string. Passes through None/non-strings unchanged."""
    if not isinstance(text, str):
        return text
    return re.sub(r'<[^>]+>', '', text)


def get_hackathons(query: str, status: str = "open", challenge_type: str = "all", limit: int = 10) -> list[dict]:
    """
    Search Devpost's hackathon listings and return results in the shared schema.
    Returns [] on any request/network error instead of raising.
    """
    params = {
        "search": query,
        "status[]": status,
    }
    if challenge_type != "all":
        params["challenge_type[]"] = challenge_type

    try:
        resp = requests.get(BASE_URL, params=params, headers={"Accept": "application/json"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[devpost_client] request failed: {e}")
        return []

    hackathons = data.get("hackathons", [])[:limit]

    results = []
    for hackathon in hackathons:
        location = (hackathon.get("displayed_location") or {}).get("location")
        themes = [t.get("name") for t in hackathon.get("themes", []) if isinstance(t, dict)]
        results.append({
            "title": hackathon.get("title"),
            "platform": "devpost",
            "url": hackathon.get("url"),
            "prize_money": _strip_html(hackathon.get("prize_amount")),
            "deadline": hackathon.get("submission_period_dates"),
            "location": location,
            "registration_status": hackathon.get("open_state"),
            "themes": themes,
        })
    return results


def enrich_with_detail_page(hackathon: dict) -> dict:
    """
    Devpost's list endpoint doesn't include team size or the full eligibility
    text. Fetch the hackathon's own page for that.

    Swap in Anakin's URL Scraper here once you have your API key.
    """
    # resp = anakin_client.scrape(hackathon["url"])
    # hackathon["team_size"] = extract_team_size(resp.text)
    return hackathon


if __name__ == "__main__":
    results = get_hackathons("robotics AI", status="open")
    for r in results:
        print(r["title"], "-", r["prize_money"], "-", r["deadline"])