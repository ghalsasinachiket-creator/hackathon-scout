"""
reasoning.py
One LLM call over the already-fetched, deduped results: decides which
are relevant and writes a short "why" note for each one kept.

The model only returns a lightweight decision per item (index + why),
never asked to re-generate the full record. This keeps the output
small regardless of how many sources/items get added - asking it to
echo every field back was overflowing the output length and
truncating the JSON once Devfolio pushed the result count up.
"""
import json
from openai import OpenAI
from config import get_secret

GROQ_API_KEY = get_secret("GROQ_API_KEY")

MODEL = "openai/gpt-oss-20b"


def reason_over_results(goal: str, results: list[dict]) -> list[dict]:
    if not results:
        return results

    if not GROQ_API_KEY:
        print("reasoning step skipped: GROQ_API_KEY is not configured")
        return [
            {
                **item,
                "why": "Reasoning skipped because GROQ_API_KEY is not configured.",
            }
            for item in results
        ]

    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

    # Only send what the model needs to judge relevance, not the full record
    slim = [
        {"index": i, "title": r.get("title"), "platform": r.get("platform"), "tags": r.get("tags")}
        for i, r in enumerate(results)
    ]

    prompt = f"""You are filtering hackathon search results for relevance.

Goal: "{goal}"

Results:
{json.dumps(slim, indent=2)}

Return ONLY a JSON array, no other text. One object per result you're
KEEPING (omit ones that aren't genuinely relevant). Each object must
have exactly these two fields:
- "index": the original index number from the list above
- "why": one short sentence on why it matches the goal
"""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=2000,
        )
        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw

        decisions = json.loads(raw)

        output = []
        for d in decisions:
            idx = d.get("index")
            if idx is not None and 0 <= idx < len(results):
                item = dict(results[idx])  # copy - never mutate the original
                item["why"] = d.get("why")
                output.append(item)

        if output:
            return output

        return [
            {
                **item,
                "why": "Reasoning did not return a usable selection, so this item is shown from the raw search results.",
            }
            for item in results
        ]

    except Exception as e:
        print(f"reasoning step failed, falling back to unfiltered results: {e}")
        return [
            {
                **item,
                "why": "Reasoning failed, so this item is shown from the raw search results.",
            }
            for item in results
        ]
