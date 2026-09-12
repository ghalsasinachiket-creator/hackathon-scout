"""
agent.py
Calls each platform client directly, merges and dedupes the results,
reasons over them, then browses into only the top-ranked results for
detail-page fields the list APIs don't provide.
"""
from clients.devpost_client import get_hackathons
from clients.unstop_client import search_unstop_hackathons
from clients.devfolio_client import search_devfolio_hackathons
from reasoning import reason_over_results
from anakin_enrich import enrich_with_detail_page

ENRICH_TOP_N = 5


def run(goal: str, limit: int = 10) -> list[dict]:
    devpost_results = get_hackathons(query=goal, status="open", limit=limit)
    unstop_results = search_unstop_hackathons(query=goal, limit=limit)
    devfolio_results = search_devfolio_hackathons(query=goal, limit=limit)

    combined = devpost_results + unstop_results + devfolio_results

    # Dedupe in case the same hackathon appears on multiple platforms
    seen = set()
    deduped = []
    for item in combined:
        key = item.get("title", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)

    reasoned = reason_over_results(goal, deduped)

    # Only browse into the pages actually worth showing - a real decision
    # based on what reasoning found, not a fixed step applied to everyone.
    for r in reasoned[:ENRICH_TOP_N]:
        enrich_with_detail_page(r)

    return reasoned


if __name__ == "__main__":
    goal = input("What are you looking for? ")
    for r in run(goal):
        print(r["title"], "-", r.get("platform"), "-", r.get("team_size"))