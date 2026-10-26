import os

print("=" * 50)
print("🐳 Generating Production Docker Architecture")
print("=" * 50)

# 1. Dockerfile.backend
DOCKERFILE_BACKEND = """FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    build-essential \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-build vector database during build
RUN python build_kb.py

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
"""

# 2. Dockerfile.frontend
DOCKERFILE_FRONTEND = """FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \\
    PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir streamlit requests

COPY ui.py .

EXPOSE 8501

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \\
  CMD curl -f http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "ui.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""

# 3. docker-compose.yml
DOCKER_COMPOSE = """version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    container_name: techzone_ai_backend
    ports:
      - "8000:8000"
    env_file:
      - .env
    volumes:
      - ./kb:/app/kb
      - ./logs:/app/logs
    restart: unless-stopped

  frontend:
    build:
      context: .
      dockerfile: Dockerfile.frontend
    container_name: techzone_ai_frontend
    ports:
      - "8501:8501"
    environment:
      - BACKEND_URL=http://backend:8000/api/v1/chat
      - TOKEN_URL=http://backend:8000/api/v1/auth/mock-token
    depends_on:
      backend:
        condition: service_healthy
    restart: unless-stopped
"""

# 4. Updated Docker-ready ui.py
DOCKER_UI_PY = """import os
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
"""

files_to_create = {
    "Dockerfile.backend": DOCKERFILE_BACKEND,
    "Dockerfile.frontend": DOCKERFILE_FRONTEND,
    "docker-compose.yml": DOCKER_COMPOSE,
    "ui.py": DOCKER_UI_PY,
}

for filename, content in files_to_create.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [file] {filename}")

print("\n" + "=" * 50)
print("  DONE! Created all Docker configuration files.")
print("=" * 50)