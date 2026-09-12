"""
unstop_client.py
Uses the "Unstop API" wrapper on RapidAPI — a real documented REST API,
no headless browser needed for Unstop.
"""
import os
import requests
from dotenv import load_dotenv
from schema import Opportunity
import re

load_dotenv()

RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
HOST = "unstop-api.p.rapidapi.com"
HEADERS = {
    "Content-Type": "application/json",
    "X-RapidAPI-Key": RAPIDAPI_KEY,
    "X-RapidAPI-Host": HOST,
}
import re

def _title_matches(title: str, query: str) -> bool:
    words = query.lower().split()
    title_lower = title.lower()
    return any(re.search(rf'\b{re.escape(w)}\b', title_lower) for w in words)

def search_unstop_hackathons(query: str, limit: int = 10) -> list[Opportunity]:
    try:
        resp = requests.get(
            f"https://{HOST}/hackathons",
            headers=HEADERS,
            params={"page": 1},  # "search" confirmed to have no effect — filtering below instead
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"[unstop_client] request failed: {e}")
        return []

    all_results = data.get("results", [])

    query_lower = query.lower()
    #matches = [item for item in all_results if query_lower in item.get("title", "").lower()]
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
            "team_size": None,  # needs enrich_with_detail_page, same as Devpost
            "registration_status": "open" if item.get("regn_open") else "closed",
            "tags": [],  # not available from this endpoint
            "source_query": query,
        })
    return output


if __name__ == "__main__":
    for r in search_unstop_hackathons("AI robotics"):
        print(r["title"], "-", r["url"])
