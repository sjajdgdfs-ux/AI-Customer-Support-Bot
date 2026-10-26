import streamlit as st
import asyncio
from app.agent import chat

st.set_page_config(
    page_title="TechZone AI Support",
    page_icon="🛒",
    layout="centered"
)

st.title("🛒 TechZone AI Support")
st.caption("Ask about products, shipping, returns, or warranties!")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Type your question here..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            reply = asyncio.run(chat(prompt))
        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
