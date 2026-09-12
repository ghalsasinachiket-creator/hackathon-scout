"""
anakin_enrich.py
Fetches a shortlisted hackathon's own event page via Anakin's URL
Scraper and pulls out team size - the one field none of the three
source APIs provide in their list/search responses.

CONFIRMED (tested directly): POST https://api.anakin.io/v1/url-scraper
with an X-API-Key header returns 202 + {"jobId": ..., "status": "pending"}.
It's asynchronous - you then poll GET .../v1/url-scraper/{jobId} until
status is "completed".

STILL UNCONFIRMED: the exact field name holding the markdown content
once a job completes. The code below checks a few likely candidates
and, if none match, raises an error printing the full response so you
can see the real structure in one shot rather than guessing again.
"""
import re
import time
import requests
from config import get_secret

ANAKIN_API_KEY = get_secret("ANAKIN_API_KEY")
BASE_URL = "https://api.anakin.io/v1/url-scraper"


def _scrape_page(url: str, timeout: int = 30, poll_interval: int = 2) -> str:
    """Submit a scrape job and poll until it completes, returning markdown."""
    submit = requests.post(
        BASE_URL,
        headers={"X-API-Key": ANAKIN_API_KEY},
        json={"url": url, "useBrowser": False},
        timeout=15,
    )
    submit.raise_for_status()
    job_id = submit.json()["jobId"]

    elapsed = 0
    while elapsed < timeout:
        time.sleep(poll_interval)
        elapsed += poll_interval

        poll = requests.get(f"{BASE_URL}/{job_id}", headers={"X-API-Key": ANAKIN_API_KEY}, timeout=15)
        poll.raise_for_status()
        data = poll.json()
        status = data.get("status")

        if status == "completed":
            for key in ("markdown", "content", "result"):
                if key in data:
                    value = data[key]
                    if isinstance(value, dict):
                        return value.get("markdown") or value.get("content") or str(value)
                    return value
            raise RuntimeError(f"Job completed but no known content field. Full response: {data}")

        if status == "failed":
            raise RuntimeError(f"Anakin scrape job failed: {data}")

    raise TimeoutError(f"Job {job_id} did not complete within {timeout}s")


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
    if not ANAKIN_API_KEY:
        print("enrichment skipped: ANAKIN_API_KEY is not configured")
        return hackathon

    try:
        markdown = _scrape_page(hackathon["url"])
        hackathon["team_size"] = _extract_team_size(markdown)
    except Exception as e:
        print(f"enrichment failed for {hackathon.get('url')}: {e}")
    return hackathon
