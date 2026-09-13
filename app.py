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


st.title("Opportunity Scout")
query = st.text_input("Search for hackathons by keyword (e.g. 'AI', 'robotics', 'blockchain'):")

if st.button("Run agent"):
    if not query:
        st.warning("Please enter a search query.")
        st.session_state.pop("results", None)
    else:
        with st.spinner("Searching Devpost and Unstop and Devfolio..."):
            st.session_state["results"] = agent.run(query)

# Deliberately outside the button's if-block: clicking the download button
# below also triggers a rerun, and on that rerun "Run agent" wasn't clicked -
# if this block lived inside that if-statement, it would vanish the instant
# you clicked download, and the file would never actually get served.
if "results" in st.session_state:
    results = st.session_state["results"]

    if not results:
        st.info("No matching hackathons found.")
    else:
        st.success(f"Found {len(results)} matching hackathons.")

        ics_content = generate_ics(results)
        st.download_button(
            "Add deadlines to calendar (.ics)", ics_content,
            "hackathon_deadlines.ics", "text/calendar"
        )

        st.dataframe(order_result_columns(results), use_container_width=True)