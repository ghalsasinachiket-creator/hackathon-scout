"""
Saves each run's results and diffs against the previous run for the same query, so that
the agent can flag what's new since the last time
"""
import json
from pathlib import Path
from datetime import datetime, timezone

SNAPSHOT_DIR = Path(__file__).parent.parent / "data" 
SNAPSHOT_DIR.mkdir(exist_ok = True)

def _snapshot_path(query: str) -> Path:
    safe_name = query.lower().replace("", "_")
    return SNAPSHOT_DIR / f"{safe_name}.json"

def save_snapshot(query: str, results: list[dict]) -> None:
    path = _snapshot_path(query)
    payload = {"checked_at": datetime.now(timezone.utc).isoformat(), "results": results}
    path.write_text(json.dumps(payload, indent=2))

def diff_against_last(query: str , new_results: list[dict]) -> list[dict]:
    path = _snapshot_path(query)
    if not path.exists():
        return new_results #First run for this query, so everything is new

    old = json.loads(path.read_text())
    old_urls = {r["url"] for r in old["results"]}
    return [r for r in new_results if r["url"] not in old_urls]