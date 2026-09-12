"""
agent.py
Calls each platform client directly, merges and dedupes the results,
then runs one reasoning pass over them before returning.
"""
from clients.devpost_client import get_hackathons
from clients.unstop_client import search_unstop_hackathons
from clients.devfolio_client import search_devfolio_hackathons
from reasoning import reason_over_results


def run(goal: str, limit: int = 10) -> list[dict]:
    devpost_results = get_hackathons(query=goal, status="open", limit=limit)
    unstop_results = search_unstop_hackathons(query=goal, limit=limit)
    devfolio_results = search_devfolio_hackathons(query=goal, limit=limit)

    combined = devpost_results + unstop_results+ devfolio_results

    # Dedupe in case the same hackathon appears on both platforms
    seen = set()
    deduped = []
    for item in combined:
        key = item.get("title", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)

    return reason_over_results(goal, deduped)


if __name__ == "__main__":
    goal = input("What are you looking for? ")
    for r in run(goal):
        print(r["title"], "-", r.get("platform"), "-", r.get("url"))