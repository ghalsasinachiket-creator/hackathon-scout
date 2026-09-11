"""Shared record shapes every client (devpost_client, unstop_client) returns
Keeping this in one place makes it easier to add new clients later, and to combine results from multiple sources into a single list.


"""
from typing import TypedDict, Optional, List

class Opportunity(TypedDict):
    title: str
    platform: str   # "devpost" | "unstop"
    url: str
    prize_money: Optional[str]
    deadline: Optional[str]
    team_size: Optional[str]
    registration_status: Optional[str]
    tags: List[str]
    source_query: str