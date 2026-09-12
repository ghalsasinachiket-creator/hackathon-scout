"""
anakin_enrich.py
Fetches a shortlisted hackathon's own event page via Anakin's URL
Scraper and pulls out team size - the one field none of the three
source APIs provide in their list/search responses.

VERIFY BEFORE TRUSTING THIS: Anakin's own docs and third-party
write-ups disagree on the exact shape - some show
api.anakin.io/v1/scrape returning {"content": ...} synchronously,
others show api.anakin.io/v1/url-scraper as an async job you poll.
You noted ANAKIN_API_KEY is already "set up and tested" - if that
test used a different endpoint/response shape than what's below,
use that one instead of this best guess.
"""
import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()

ANAKIN_API_KEY = os.environ["ANAKIN_API_KEY"]


def _scrape_page(url: str) -> str:
    """Fetch a single URL as clean markdown via Anakin's URL Scraper."""
    resp = requests.post(
        "https://api.anakin.io/v1/scrape",  # TODO: confirm against your tested call
        headers={"X-API-Key": ANAKIN_API_KEY},
        json={"url": url, "format": "markdown"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["content"]  # TODO: confirm this key name too


def _extract_team_size(markdown: str) -> str | None:
    """Rough heuristic - looks for common team-size phrasing on the page."""
    match = re.search(
        r"team\s*(?:size|of)?\s*[:\-]?\s*(\d+(?:\s*-\s*\d+)?)\s*(?:members|people)?",
        markdown,
        re.IGNORECASE,
    )
    return match.group(1) if match else None


def enrich_with_detail_page(hackathon: dict) -> dict:
    """Fetch the hackathon's own page and fill in what the list APIs don't give us."""
    try:
        markdown = _scrape_page(hackathon["url"])
        hackathon["team_size"] = _extract_team_size(markdown)
    except Exception as e:
        print(f"enrichment failed for {hackathon.get('url')}: {e}")
        # leave team_size as-is rather than breaking the run over one bad page
    return hackathon