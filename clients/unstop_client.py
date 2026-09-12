"""
unstop_client.py
Uses the "Unstop API" wrapper on RapidAPI — a real documented REST API,
no headless browser needed for Unstop.
"""
import os
import requests
from dotenv import load_dotenv
from schema import Opportunity

load_dotenv()

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
HOST = "unstop-api.p.rapidapi.com"
HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": HOST,
}


def search_unstop_hackathons(query: str, limit: int = 10) -> list[Opportunity]:
    # TODO: confirm "search" is a real param — RapidAPI's Params tab showed
    # only 1 param (likely just "page"). If unsupported, filter `results`
    # by query client-side instead.
    try:
        resp = requests.get(
            f"https://{HOST}/hackathons",
            headers=HEADERS,
            params={"page": 1, "search": query},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        import json
        print(json.dumps(data,indent =2))
    except requests.exceptions.RequestException as e:
        print(f"[unstop_client] request failed: {e}")
        return []

    # TODO: check "Example Responses" in RapidAPI to confirm real key names.
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