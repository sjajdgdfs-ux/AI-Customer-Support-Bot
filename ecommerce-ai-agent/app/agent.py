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

from app.rag import search_knowledge
from app.security import SecurityShield

# 📍 مسارات مطلقة ديناميكية لتفادي أخطاء السيرفرات السحابية
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")

DEFAULT_PRODUCTS = [
    {"name": "iPhone 15 Pro Max 256GB", "price": 1199, "category": "Smartphones", "warranty": "1-year Apple warranty", "availability": "In Stock"},
    {"name": "Samsung Galaxy S24 Ultra", "price": 1419, "category": "Smartphones", "warranty": "1-year Samsung warranty", "availability": "In Stock"},
    {"name": "MacBook Air M3 15-inch", "price": 1299, "category": "Laptops", "warranty": "1-year Apple warranty", "availability": "In Stock"},
    {"name": "AirPods Pro 2", "price": 249, "category": "Audio", "warranty": "1-year Apple warranty", "availability": "In Stock"}
]


def extract_text(content) -> str:
    """استخراج النص سواء كان str أو قائمة"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(item["text"])
            else:
                parts.append(str(item))
        return " ".join(parts)
    return str(content)


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str


VALID_INTENTS = {"policy", "product", "greeting", "complaint", "other"}


async def async_search_policy_tool(query: str) -> str:
    return await asyncio.to_thread(search_knowledge, query)


async def async_search_product_tool(query: str) -> str:
    def _search():
        os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.exists(PRODUCTS_PATH):
            try:
                with open(PRODUCTS_PATH, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_PRODUCTS, f, indent=2)
            except Exception:
                pass
            products = DEFAULT_PRODUCTS
        else:
            try:
                with open(PRODUCTS_PATH, "r", encoding="utf-8") as f:
                    products = json.load(f)
            except Exception:
                products = DEFAULT_PRODUCTS

        q = query.lower()
        GENERAL_KEYWORDS = ["product", "products", "catalog", "catalogue", "sell", "available", "list", "have", "offer", "items"]

        if any(kw in q for kw in GENERAL_KEYWORDS):
            return json.dumps(products, ensure_ascii=False, indent=2)

        tokens = [t for t in q.replace("?", " ").replace(",", " ").split() if len(t) > 2]
        results = [p for p in products if any(token in f"{p['name']} {p['category']}".lower() for token in tokens)]

        return json.dumps(results or products, ensure_ascii=False, indent=2)

    return await asyncio.to_thread(_search)


# 🔑 قراءة مفتاح الـ API من البيئة أو من Streamlit Secrets
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    try:
        import streamlit as st
        api_key = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        pass

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=api_key,
    temperature=0.2,
    max_output_tokens=512
)

shield = SecurityShield()


async def classify_intent(state: AgentState) -> AgentState:
    user_msg = shield.sanitize_input(extract_text(state["messages"][-1].content))
    prompt = (
        "Classify this customer message into ONE word:\n"
        "policy, product, greeting, complaint, or other.\n\n"
        f"Message: \"{user_msg}\"\n\nCategory:"
    )

    response = await llm.ainvoke([HumanMessage(content=prompt)])
    raw = extract_text(response.content).strip().lower()

    intent = "other"
    for candidate in VALID_INTENTS:
        if candidate in raw:
            intent = candidate
            break

    return {"intent": intent}


async def handle_query(state: AgentState) -> AgentState:
    raw_user_msg = extract_text(state["messages"][-1].content)
    clean_msg = shield.redact_pii(shield.sanitize_input(raw_user_msg))

    if shield.is_injection(clean_msg):
        return {"messages": [AIMessage(content="I cannot fulfill this request due to security policies.")]}

    intent = state.get("intent", "other")
    sys_prompt = "You are TechZone's support agent. Be concise, friendly, and helpful. Answer ONLY using provided context.\n"

    if intent == "policy":
        context = await async_search_policy_tool(clean_msg)
        sys_prompt += f"\n\nStore Policies:\n{context}"
    elif intent == "product":
        context = await async_search_product_tool(clean_msg)
        sys_prompt += f"\n\nProduct Catalog:\n{context}\nFormat product names and prices nicely."
    elif intent == "greeting":
        return {"messages": [AIMessage(content="Welcome to TechZone Electronics! 🛒 How can I help you today?")]}
    elif intent == "complaint":
        sys_prompt += "\n\nApologize sincerely, empathize, and offer contact at support@techzone.com."

    messages = [SystemMessage(content=sys_prompt), *state["messages"]]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_intent)
    graph.add_node("respond", handle_query)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "respond")
    graph.add_edge("respond", END)
    return graph


app_graph = build_graph().compile()


async def chat(user_input: str, thread_id: str = "default_session") -> str:
    """الدالة الرئيسية للشات"""
    try:
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
        os.makedirs(os.path.join(BASE_DIR, "kb"), exist_ok=True)
        db_file = os.path.join(BASE_DIR, "kb", "chat_memory.db")
        async with AsyncSqliteSaver.from_conn_string(db_file) as checkpointer:
            compiled = build_graph().compile(checkpointer=checkpointer)
            result = await compiled.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": thread_id}}
            )
            return extract_text(result["messages"][-1].content)
    except Exception:
        # Fallback بسيط لو الـ Checkpointer حصل فيه مشكلة على الكلاود
        result = await app_graph.ainvoke({"messages": [HumanMessage(content=user_input)]})
        return extract_text(result["messages"][-1].content)