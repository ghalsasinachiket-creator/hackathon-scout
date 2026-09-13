"""
app.py
Streamlit dashboard -> the entry pint for the demo.Fill this in during step 7 once agent.py can run end-to-end.
"""
import streamlit as st
import agent
from calendar_export import generate_ics

st.title("Opportunity Scout")
query = st.text_input("Search for hackathons by keyword (e.g. 'AI', 'robotics', 'blockchain'):")


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
    #st.write("TODO: call agent.run(query) and display the results table")
    if not query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching Devpost and Unstop and Devfolio..."):
            results = agent.run(query)

        if not results:
            st.info("No matching hackathons found.")
        else:
            st.success(f"Found {len(results)} matching hackathons.")
            ics_content = generate_ics(results)
            st.download_button(
                "Add deadlines to calendar (.ics)", ics_content,                    # <-- add this
                "hackathon_deadlines.ics", "text/calendar"   
            )
            st.dataframe(order_result_columns(results), use_container_width=True)
