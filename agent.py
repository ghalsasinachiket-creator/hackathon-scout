"""
agent.py
The tool calling loop: gives Claude a goal and 2 tools (search_devpost_hackathons and search_unstop_hackathons) to use to achieve it.
"""
import os
import json
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from clients.devpost_client import get_hackathons
from clients.unstop_client import search_unstop_hackathons

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-5"

TOOLS = [
    {
        "name": "search_devpost_hackathons",
        "description": (
            "Search Devpost's hackathon listings by keyword. Devpost hosts hackathons "
            "internationally. Returns title, url, prize money, deadline, location, "
            "registration status, and themes for each match."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword(s) to search for, e.g. 'AI', 'robotics', 'blockchain'.",
                },
                "status": {
                    "type": "string",
                    "enum": ["open", "upcoming", "ended"],
                    "description": "Filter by registration status. Defaults to 'open'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of results to return. Defaults to 10.",
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_unstop_hackathons",
        "description": (
            "Search Unstop's hackathon listings by keyword. Unstop specializes in hackathons "
            "hosted at Indian colleges and universities. Returns title, url, prize info, "
            "deadline, location, and registration status. Note: only scans the most recently "
            "approved page of listings, so a niche query may return few results even if "
            "matching hackathons exist."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Keyword(s) to search for, e.g. 'AI', 'robotics', 'blockchain'.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Max number of results to return. Defaults to 10.",
                },
            },
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = """You are Opportunity Scout, an assistant that helps users find hackathons matching their interests.

You have two tools: search_devpost_hackathons (international hackathons) and search_unstop_hackathons (hackathons at Indian colleges/universities, only covers the most recent page of listings).

When the user describes what they're looking for, call BOTH tools with the same keyword(s) so you cover both platforms, then combine the results into a single list. Deduplicate by title/url if the same hackathon appears on both. Present each result with its title, platform, deadline, prize (if known), and a link. If a field wasn't returned by a tool, say so rather than guessing.

If neither tool returns any matches, say so plainly rather than inventing hackathons."""


def execute_tool(name: str, tool_input: dict):
    query = tool_input.get("query", "")
    limit = tool_input.get("limit", 10)

    if name == "search_devpost_hackathons":
        return get_hackathons(query=query, status=tool_input.get("status", "open"), limit=limit)
    elif name == "search_unstop_hackathons":
        return search_unstop_hackathons(query=query, limit=limit)
    else:
        return {"error": f"Unknown tool: {name}"}


def run(goal: str, max_turns: int = 5) -> str:
    messages = [{"role": "user", "content": goal}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            text_blocks = [b.text for b in response.content if b.type == "text"]
            return "\n".join(text_blocks)

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result),
                })
        messages.append({"role": "user", "content": tool_results})

    return "Reached max turns without a final answer."


if __name__ == "__main__":
    goal = input("What are you looking for? ")
    print(run(goal))