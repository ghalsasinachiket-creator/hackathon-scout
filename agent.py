"""
agent.py
Calls both platform clients directly and merges the results — no LLM
needed for a straightforward keyword search across fixed sources.
"""
from clients.devpost_client import get_hackathons
from clients.unstop_client import search_unstop_hackathons


def run(goal: str, limit: int = 10) -> list[dict]:
    devpost_results = get_hackathons(query=goal, status="open", limit=limit)
    unstop_results = search_unstop_hackathons(query=goal, limit=limit)

    combined = devpost_results + unstop_results

    # Dedupe in case the same hackathon appears on both platforms
    seen = set()
    deduped = []
    for item in combined:
        key = item.get("title", "").strip().lower()
        if key and key not in seen:
            seen.add(key)
            deduped.append(item)

    return deduped


if __name__ == "__main__":
    goal = input("What are you looking for? ")
    for r in run(goal):
        print(r["title"], "-", r.get("platform"), "-", r.get("url"))