"""
reasoning.py
One LLM call over the already-fetched, deduped results: drops weak
matches and attaches a short "why" note to each one that's kept.
This is the piece that turns agent.py from a keyword-matching script
into something that's actually reasoning about the results.
"""
import os
import json

from openai import OpenAI

client = OpenAI(
    api_key=os.environ["GROQ_API_KEY"],
    base_url="https://api.groq.com/openai/v1",
)
# Groq's model catalog changes fairly often - verify this is still current
# at console.groq.com/docs/models before relying on it for the demo.
MODEL = "openai/gpt-oss-20b"


def reason_over_results(goal: str, results: list[dict]) -> list[dict]:
    if not results:
        return results

    prompt = f"""You are filtering hackathon search results for relevance.
Goal: "{goal}"
Results (JSON):
{json.dumps(results, indent=2)}
Return ONLY a JSON array, no other text. Each item must include all of
its original fields plus a new "why" field: one short sentence on why
it matches the goal. Drop any result that is not genuinely relevant.
"""
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()

        # Some models wrap JSON in markdown-style code fences, so strip those if present
        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw
        return json.loads(raw)
    except Exception as e:
        print(f"Reasoning failed, falling back to unfiltered results: {e}")
        return results