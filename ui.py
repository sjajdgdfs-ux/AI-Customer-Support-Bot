import os
import streamlit as st
import requests
import uuid

# Environment variables injected by Docker Compose
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/chat")
TOKEN_URL = os.getenv("TOKEN_URL", "http://localhost:8000/api/v1/auth/mock-token")

st.set_page_config(page_title="TechZone AI Support", page_icon="🛒", layout="centered")
st.title("🛒 TechZone AI Support")
st.caption("Containerized Enterprise Architecture (Docker)")

# 1. Fetch JWT Token on startup
if "access_token" not in st.session_state:
    try:
        res = requests.get(TOKEN_URL, timeout=5)
        st.session_state.access_token = res.json()["access_token"]
    except Exception as e:
        st.error(f"Cannot connect to Backend service at {TOKEN_URL}")
        st.stop()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar info
with st.sidebar:
    st.header("⚙️ Container Status")
    st.success(" Backend: Online")
    st.success(" Auth: JWT Verified")
    st.text(f"Session: {st.session_state.session_id[:8]}...")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about products or store policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing through secure agent..."):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                payload = {"message": prompt, "session_id": st.session_state.session_id}
                
                response = requests.post(BACKEND_URL, json=payload, headers=headers, timeout=30)
                
                if response.status_code == 200:
                    reply = response.json()["reply"]
                elif response.status_code == 429:
                    reply = "⚠️ Rate limit exceeded. Please wait a moment."
                else:
                    reply = f"⚠️ Server Error ({response.status_code}): {response.text}"
            except Exception as e:
                reply = f"❌ Network Connection Error: {str(e)}"
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
