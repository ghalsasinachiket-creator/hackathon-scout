import requests

for status in ["open", "upcoming", None]:
    params = {"search": "Blockchain"}
    if status:
        params["status[]"] = status
    resp = requests.get(
        "https://devpost.com/api/hackathons",
        params=params,
        headers={"Accept": "application/json"},
        timeout=10,
    )
    data = resp.json()
    hackathons = data.get("hackathons", [])
    print(f"status={status}: {len(hackathons)} results")
    for h in hackathons[:5]:
        print("  -", h.get("title"))