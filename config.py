"""
Configuration helpers shared by the Streamlit app and local scripts.

Local development can keep using .env. Streamlit Cloud should define the
same keys in app secrets.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).parent / "clients" / ".env")


def get_secret(name: str) -> str | None:
    """Return a config value from env vars first, then Streamlit secrets."""
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st

        value = st.secrets.get(name)
        return str(value) if value else None
    except Exception:
        return None
