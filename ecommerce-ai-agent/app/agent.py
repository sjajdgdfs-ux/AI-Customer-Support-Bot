import json
import os
import asyncio
from typing import TypedDict, Annotated
from dotenv import load_dotenv

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.rag import search_knowledge, ensure_data_exists
from app.security import SecurityShield

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")

def extract_text(content) -> str:
    if isinstance(content, str): return content
    if isinstance(content, list):
        return " ".join(item if isinstance(item, str) else item.get("text", "") for item in content if isinstance(item, (str, dict)))
    return str(content)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# ⚡ Fast Local Search for Products
def search_products_fast(query: str) -> str:
    ensure_data_exists()
    try:
        with open(PRODUCTS_PATH, "r", encoding="utf-8") as f: products = json.load(f)
    except Exception:
        products = []
    
    q = query.lower()
    if any(k in q for k in ["product", "catalog", "sell", "available", "list", "item", "have", "offer"]):
        return json.dumps(products, ensure_ascii=False, indent=2)
    
    tokens = [t for t in q.replace("?", " ").split() if len(t) > 2]
    results = [p for p in products if any(t in f"{p['name']} {p.get('category','')}".lower() for t in tokens)]
    return json.dumps(results or products, ensure_ascii=False, indent=2)

# API Key setup
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except Exception: pass

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=api_key,
    temperature=0.2,
    max_output_tokens=300
)

shield = SecurityShield()

# ⚡ Ultra-fast single-node handler
async def handle_query(state: AgentState) -> AgentState:
    user_msg = extract_text(state["messages"][-1].content)
    clean_msg = shield.sanitize_input(user_msg)

    # 1. Security Check
    if shield.is_injection(clean_msg):
        return {"messages": [AIMessage(content="Request blocked due to security policy.")]}

    q_lower = clean_msg.lower().strip()

    # 2. 🚀 Instant Greeting (0.01 seconds - NO LLM CALL)
    if q_lower in ["hi", "hello", "hey", "hi there", "hello there", "thanks", "thank you"]:
        return {"messages": [AIMessage(content="Welcome to TechZone Electronics! 🛒 How can I help you today? Ask me about products, shipping, or returns!")]}

    # 3. 🚀 Fast Smart Context Retrieval
    context = ""
    if any(k in q_lower for k in ["shipping", "return", "policy", "warranty", "pay", "deliver", "refund"]):
        context = f"STORE POLICIES:\n{await asyncio.to_thread(search_knowledge, clean_msg)}"
    else:
        context = f"PRODUCT CATALOG:\n{search_products_fast(clean_msg)}"

    # 4. Single LLM Response Call
    sys_prompt = f"""You are TechZone's friendly AI support agent.
    RULES:
    - Be brief and helpful.
    - Use ONLY this context to answer:
    {context}
    """

    messages = [SystemMessage(content=sys_prompt), *state["messages"]]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}

# ⚡ Simple Graph
def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("respond", handle_query)
    graph.add_edge(START, "respond")
    graph.add_edge("respond", END)
    return graph

app_graph = build_graph().compile()

async def chat(user_input: str, thread_id: str = "default_session") -> str:
    result = await app_graph.ainvoke({"messages": [HumanMessage(content=user_input)]})
    return extract_text(result["messages"][-1].content)