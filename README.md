# 🤖 TechZone AI: Production-Ready E-commerce Support Agent

A professional AI Customer Support Agent built with **LangGraph**, **Gemini **, and **Streamlit**. This agent handles routine inquiries, searches product catalogs, and includes enterprise-grade security guardrails.

🚀 **Live Demo:**[https://ai-customer-support-bot-gkubgfmeimow5j7reeens4.streamlit.app/]
📺 **Video Demo:** [https://www.loom.com/share/997793f6db154fd9abdb5101bb8a7e35]

## 🌟 Key Features

- **Smart RAG (Retrieval-Augmented Generation):** Answers policy questions (returns, shipping) using localized knowledge.
- **Real-time Product Search:** Connected to a product database to provide stock and pricing info.
- **Security Shield:** Built-in protection against Prompt Injections and PII data leakage.
- **Stateful Conversations:** Remembers context using LangGraph's checkpointer.
- **Fast Performance:** Optimized with caching and instant greeting bypass (< 1s response time).

## 🛠️ Tech Stack

- **Framework:** LangGraph / LangChain
- **LLM:** Google Gemini
- **Frontend:** Streamlit
- **Vector Store:** ChromaDB
- **Security:** Custom Regex & LLM-based Guardrails
- **Deployment:** Docker & Streamlit Cloud

## 🚀 How to Run Locally

1. **Clone the repo:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ecommerce-ai-agent.git
   cd ecommerce-ai-agent
   ```
