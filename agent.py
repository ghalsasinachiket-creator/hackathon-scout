"""
agent.py
The tool calling loop: gives Claude a goal and 2 tools (search_devpost_hackathons and search_unstop_hackathons) to use to achieve it.
"""
import os
from dotenv import load_dotenv
load_dotenv()

from anthropic import Anthropic
from clients.devpost_client import get_hackathons
from clients.unstop_client import search_unstop_hackathons

client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TOOLS = [
    {
        "name": "search_devpost",
        "description": "Search Devpost for hackathons matching a query.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords."},
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "minimum": 1,
                    "maximum": 25,
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
    {
        "name": "search_unstop",
        "description": "Search Unstop for hackathons matching a query.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search keywords."},
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return.",
                    "minimum": 1,
                    "maximum": 25,
                    "default": 10,
                },
            },
            "required": ["query"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are Opportunity Scout. Find relevant hackathons using the available "
    "tools, then return a concise ranked list with title, platform, deadline, "
    "prize, team size, tags, and URL when available."
)


def _call_tool(name: str, tool_input: dict) -> list[dict]:
    query = tool_input["query"]
    limit = tool_input.get("limit", 10)

    if name == "search_devpost":
        return get_hackathons(query=query, limit=limit)
    if name == "search_unstop":
        return search_unstop_hackathons(query=query, limit=limit)

    raise ValueError(f"Unknown tool: {name}")


def run(goal: str, max_turns: int = 4) -> str:
    messages = [{"role": "user", "content": goal}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="claude-3-5-sonnet-latest",
            max_tokens=1200,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        tool_uses = [block for block in response.content if block.type == "tool_use"]
        if not tool_uses:
            return "".join(
                block.text for block in response.content if block.type == "text"
            )

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use.id,
                        "content": _call_tool(tool_use.name, tool_use.input),
                    }
                    for tool_use in tool_uses
                ],
            }
        )

    return "Reached the tool-call limit before Claude returned a final answer."
