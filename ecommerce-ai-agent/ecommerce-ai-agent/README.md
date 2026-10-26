# TechZone AI Customer Support Agent

An intelligent AI customer support bot built with LangGraph, Gemini 2.0, RAG, and FastAPI.

## Features

- Intent Classification (policy, product, complaint, greeting)
- RAG-Powered Answers from ChromaDB
- Security Shield (prompt injection + PII redaction)
- Async FastAPI Backend
- Streamlit Chat UI

## Quick Start

    pip install -r requirements.txt
    # Edit .env with your API key
    python build_kb.py
    streamlit run ui.py

## Tech Stack

| Layer | Technology |
|-------|------------|
| LLM | Gemini 2.0 Flash |
| Orchestration | LangGraph |
| RAG | LangChain + ChromaDB |
| Backend | FastAPI |
| Frontend | Streamlit |
