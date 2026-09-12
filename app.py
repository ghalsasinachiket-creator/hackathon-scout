"""
app.py
Streamlit dashboard -> the entry pint for the demo.Fill this in during step 7 once agent.py can run end-to-end.
"""
import streamlit as st
import agent
st.title("Opportunity Scout")
query = st.text_input("Search for hackathons by keyword (e.g. 'AI', 'robotics', 'blockchain'):")

if st.button("Run agent"):
    #st.write("TODO: call agent.run(query) and display the results table")
    if not query:
        st.warning("Please enter a search query.")
    else:
        with st.spinner("Searching Devpost and Unstop..."):
            results = agent.run(query)

        if not results:
            st.info("No matching hackathons found.")
        else:
            st.success(f"Found {len(results)} matching hackathons.")
            st.dataframe(results, width=True)
    