"""
app.py
Streamlit dashboard - the entry point for the demo.
"""
import streamlit as st
import agent
from calendar_export import generate_ics


def order_result_columns(results: list[dict]) -> list[dict]:
    preferred = [
        "title",
        "why",
        "platform",
        "url",
        "prize_money",
        "deadline",
        "location",
        "team_size",
        "registration_status",
        "themes",
        "tags",
        "source_query",
    ]

    ordered = []
    for item in results:
        columns = {key: item.get(key) for key in preferred if key in item}
        columns.update({key: value for key, value in item.items() if key not in columns})
        ordered.append(columns)
    return ordered


#st.set_page_config(page_title="Hackathon Scout", page_icon="🔭")   #