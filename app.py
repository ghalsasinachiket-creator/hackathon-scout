"""
app.py
Streamlit dashboard -> the entry pint for the demo.Fill this in during step 7 once agent.py can run end-to-end.
"""
import streamlit as st

st.title("Opportunity Scout")
query = st.text_input("Search for hackathons by keyword (e.g. 'AI', 'robotics', 'blockchain'):")

if st.button("Run agent"):
    st.write("TODO: call agent.run(query) and display the results table")
    