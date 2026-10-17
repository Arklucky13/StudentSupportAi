
import os

import httpx
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)

st.set_page_config(
    page_title="Student Support AI",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 Student Support AI")
st.caption(
    "Your assistant for academics, careers, and learning."
)

st.write(
    "Welcome! We are building an assistant that answers "
    "student questions using trusted documents."
)

if st.button("Check backend connection"):
    try:
        response = httpx.get(
            f"{API_URL}/health",
            timeout=5.0,
        )
        response.raise_for_status()

        data = response.json()
        st.success(
            f"Backend connected: {data['status']}"
        )

    except httpx.HTTPError as error:
        st.error(
            f"Could not connect to the backend: {error}"
        )
