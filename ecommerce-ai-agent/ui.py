import os
import streamlit as st
import requests
import uuid

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1/chat")
TOKEN_URL = os.getenv("TOKEN_URL", "http://localhost:8000/api/v1/auth/mock-token")

st.set_page_config(page_title="TechZone AI Support", page_icon="🛒")
st.title("🛒 TechZone AI Support")

# 1. Fetch JWT Token on startup (Mock Login)
if "access_token" not in st.session_state:
    try:
        res = requests.get(TOKEN_URL)
        st.session_state.access_token = res.json()["access_token"]
    except:
        st.error("Backend server is offline! Start FastAPI first.")
        st.stop()

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]): st.markdown(msg["content"])

if prompt := st.chat_input("Ask about products or policies..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"): st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing securely..."):
            try:
                headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
                payload = {"message": prompt, "session_id": st.session_state.session_id}
                
                response = requests.post(BACKEND_URL, json=payload, headers=headers)
                
                if response.status_code == 200:
                    reply = response.json()["reply"]
                elif response.status_code == 429:
                    reply = "⚠️ Rate limit exceeded. Please slow down."
                else:
                    reply = f"⚠️ Auth/Server Error: {response.text}"
            except Exception as e:
                reply = "❌ Backend offline."
        st.markdown(reply)
    st.session_state.messages.append({"role": "assistant", "content": reply})