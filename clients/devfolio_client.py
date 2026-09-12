def search_devfolio_hackathons(query: str, limit: int = 10) -> list[dict]:
    try:
        resp = requests.post(
            GRAPHQL_URL,
            json={"query": QUERY, "operationName": "GetAllHackathonTypes"},
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"[devfolio_client] request failed: {e}")
        return []

    try:
        data = resp.json()
    except ValueError:
        print("[devfolio_client] response wasn't JSON — likely a Cloudflare challenge page, not real data")
        return []

    if "errors" in data:
        print(f"[devfolio_client] GraphQL errors: {data['errors']}")
        return []

    payload = data.get("data", {})
    bucketed = []
    for status_label, key in [("open", "open_hackathons"), ("upcoming", "upcoming_hackathons")]:
        for h in payload.get(key, []):
            h["_status"] = status_label
            bucketed.append(h)

    # --- new debug lines ---
    print(f"[devfolio_client] fetched {len(bucketed)} hackathons total")
    for h in bucketed:
        print(" -", h.get("name"))
    # --- end debug lines ---

    matches = [h for h in bucketed if _title_matches(h.get("name", ""), query)]  # <-- this line is "the filter step"

    output = []
    for h in matches[:limit]:
        settings = h.get("settings") or {}
        themes = [t.get("theme", {}).get("name") for t in h.get("themes", []) if isinstance(t, dict)]
        output.append({
            "title": h.get("name"),
            "platform": "devfolio",
            "url": settings.get("external_apply_url") or settings.get("site") or f"https://{h.get('slug')}.devfolio.co",
            "prize_money": None,
            "deadline": settings.get("reg_ends_at"),
            "location": "Online" if h.get("is_online") else None,
            "team_size": None,
            "registration_status": h.get("_status"),
            "tags": themes,
            "source_query": query,
        })
    return output