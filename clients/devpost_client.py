"""
devpost_client.py
Lightweight client for interacting with the Devpost API.
No API key needed
"""
import requests

BASE_URL = "https://devpost.com/api/hackathons"

def get_hackathons(query: str, status: str = "open" , challenge_type: str = "all", limit: int = 10) -> list[dict]:
    """
    Search Devpost's hackathon listings and return results in the shared schema.
 
    IMPORTANT: the param names below (search, status[], challenge_type[]) are a
    starting point. Confirm the real ones yourself: open devpost.com/hackathons
    in a browser, open DevTools -> Network, run a search there, and check the
    exact query string sent to /api/hackathons. Adjust this dict to match.
    """
    params = {
        "search": query,
        "status[]": status,
    }
    if challenge_type != "all":
        params["challenge_type[]"] = challenge_type

    resp = requests.get(BASE_URL , params=params, headers = {"Accept": "application/json"}, timeout=10)
    resp.raise_for_status()
    data = resp.json()

    hackathons = data.get("hackathons", [])[:limit]
    import json
    print(json.dumps(hackathons[0], indent=2))
    return[
        {
            "title": hackathon.get("title"),
            "platform":"devpost",
            "url":hackathon.get("url"),
            "prize_money":hackathon.get("prize_money"),
            "deadline":hackathon.get("submission_period_case"),
            "registration_status":hackathon.get("open_state"),
            "tags":hackathon.get("themes",[]),
            "team_size":None,
            "source_query":query,
        }
        for hackathon in hackathons
    ]

#def enrich_with_detail_page(hackathon: dict) -> dict:
    """Devpost's list endpoint doesn't include team size or the full eligibility
    text. Fetch the hackathon's own page for that - this is the 'click into
    the listing' step from your demo script.
 
    Swap in Anakin's URL Scraper here once you have your API key: it hands
    back clean Markdown/JSON for hackathon["url"] with anti-bot handling
    already done, which is simpler than requests + BeautifulSoup for this.
    """
    #resp = anakin_client.scrape(hackathon[https://anakin.io/products/url-scraper])
    #hackathon["team_size"] = extract_team_size(resp.text)
    #return get_hackathons

#if __name__ == "__main__":
   # results = [enrich_with_detail_page(r) for r in get_hackathons("robotics AI", status="open")]
   # for r in results:
  #     print(r["title"], "-", r["prize_money"], "-", r["deadline"], "-", r["team_size"])


def enrich_with_detail_page(hackathon: dict) -> dict:
    """
    Devpost's list endpoint doesn't include team size or the full eligibility
    text. Fetch the hackathon's own page for that - this is the 'click into
    the listing' step from your demo script.

    Swap in Anakin's URL Scraper here once you have your API key: it hands
    back clean Markdown/JSON for hackathon["url"] with anti-bot handling
    already done, which is simpler than requests + BeautifulSoup for this.
    """
    # resp = anakin_client.scrape(hackathon["url"])
    # hackathon["team_size"] = extract_team_size(resp.text)
    return hackathon


if __name__ == "__main__":
    results = get_hackathons("robotics AI", status="open")
    for r in results:
        print(r["title"], "-", r["prize_money"], "-", r["deadline"])