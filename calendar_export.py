"""
calendar_export.py
Turns the shortlist's deadlines into a downloadable .ics file - opens
directly in Google Calendar, Outlook, or Apple Calendar. This is the
concrete "take real action" step: a usable artifact, not just a table.
 
Deadline formats differ across sources - Devfolio gives clean ISO
datetimes, Devpost gives ranges like "May 22 - Sep 13, 2026" (the
deadline is the end of the range). Anything that doesn't parse is
just skipped rather than breaking the whole export.
"""

import uuid
from datetime import datetime, timezone
from dateutil import parser as date_parser

def _parse_deadline(deadline_str:str):
    if not deadline_str:
        return None
    text = str(deadline_str).strip()
    if "-" in text:
        text = text.split("-")[-1].strip()
    try:
        return date_parser.parse(text, fuzzy=True)
    except(ValueError, OverflowError):
        return None

def _format_ics_datetime(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

def generate_ics(results:list[dict]) -> str:
    """One .ics file, one VENENT  per result with a parsed deadline. Returns the .ics file as a string."""
    now = _format_ics_datetime(datetime.now(timezone.utc))
    events = []

    for r in results:
        deadline = _parse_deadline(r.get("deadline"))
        if not deadline:
            continue

        why = (r.get("why") or "").replace("\n", "")
        events.append(
             "BEGIN:VEVENT\n"
            f"UID:{uuid.uuid4()}@opportunity-scout\n"
            f"DTSTAMP:{now}\n"
            f"DTSTART:{_format_ics_datetime(deadline)}\n"
            f"SUMMARY:{r.get('title', 'Hackathon')} - Deadline\n"
            f"DESCRIPTION:{why}\n"
            f"URL:{r.get('url', '')}\n"
            "END:VEVENT"
        )

    return(
         "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Hackathon Scout//EN\n"
        + "\n".join(events)
        + "\nEND:VCALENDAR"
    )