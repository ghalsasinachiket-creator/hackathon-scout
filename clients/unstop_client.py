"""
unstop_client.py
Uses the "Unstop API" wrapper on RapidAPI instead of Playwright/Anakin
Browser Sessions — it's a real documented REST API, so no headless
browser is needed for Unstop after all.
"""
import os
import requests
from schema import Opportunity

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
HOST = "unstop-api.p.rapidapi.com"
HEADERS = {
    "Content-Type": "application/json",
    "x-rapidapi-host": HOST,
    "x-rapidapi-key": RAPIDAPI_KEY,
}

def search_unstop_hackathons(query: str, limit: int = 10) -> list[Opportunity]:
    # TODO: your screenshot only shows "Fetch Workshops" (/workshops).
    # Check the left sidebar under "Unstop API" for a separate
    # "Fetch Hackathons" / "Fetch Competitions" endpoint before assuming
    # this is the right path — workshops and hackathons may be different
    # endpoints in the same collection.
    resp = requests.get(
        f"https://{HOST}/hackathons",  # TODO: confirm against the collection
        headers=HEADERS,
        params={"page": 1, "search": query},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    # TODO: check the "Example Responses" tab in RapidAPI to confirm
    # real key names before trusting this — same rule as devpost_client.py.
    results = data.get("data", data.get("results", []))[:limit]
    return [
        {
            "title": item.get("title"),
            "platform": "unstop",
            "url": item.get("public_url") or item.get("url"),
            "prize_money": item.get("prize_money"),
            "deadline": item.get("deadline") or item.get("end_date"),
            "team_size": item.get("team_size"),
            "registration_status": item.get("status"),
            "tags": item.get("tags", []),
            "source_query": query,
        }
        for item in results
    ]


if __name__ == "__main__":
    for r in search_unstop_hackathons("AI robotics"):
        print(r["title"], "-", r["url"])