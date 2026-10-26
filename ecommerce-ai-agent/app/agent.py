import json, os, asyncio
from typing import TypedDict, Annotated
from dotenv import load_dotenv
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PRODUCTS_PATH = os.path.join(BASE_DIR, "data", "products.json")

load_dotenv()

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.rag import search_knowledge
from app.security import SecurityShield

def extract_text(content) -> str:
    if isinstance(content, str): return content
    if isinstance(content, list): return " ".join(item.get("text", "") if isinstance(item, dict) else str(item) for item in content if isinstance(item, (str, dict)))
    return str(content)

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str

# ── Non-blocking Async Tools ──
async def async_search_policy_tool(query: str) -> str:
    return await asyncio.to_thread(search_knowledge, query)

async def async_search_product_tool(query: str) -> str:
    def _search():
        if not os.path.exists(PRODUCTS_PATH):
                return "Catalog unavailable."
        with open("PRODUCTS_PATH", "r", encoding="utf-8") as f: products = json.load(f)
        q = query.lower()
        if any(kw in q for kw in ["product", "catalog", "sell", "available", "list"]):
            return json.dumps(products, ensure_ascii=False, indent=2)
        tokens = [t for t in q.replace("?", " ").split() if len(t) > 2]
        results = [p for p in products if any(token in f"{p['name']} {p['category']}".lower() for token in tokens)]
        return json.dumps(results or products, ensure_ascii=False, indent=2)
    return await asyncio.to_thread(_search)

llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite", temperature=0.2, max_output_tokens=512)
shield = SecurityShield()

# ── Async Nodes ──
async def classify_intent(state: AgentState) -> AgentState:
    user_msg = shield.sanitize_input(extract_text(state["messages"][-1].content))
    prompt = f"Classify into ONE word: policy, product, greeting, complaint, other.\nMessage: '{user_msg}'"
    response = await llm.ainvoke([HumanMessage(content=prompt)])
    intent = next((c for c in ["policy", "product", "greeting", "complaint"] if c in extract_text(response.content).lower()), "other")
    return {"intent": intent}

async def handle_query(state: AgentState) -> AgentState:
    user_msg = shield.redact_pii(shield.sanitize_input(extract_text(state["messages"][-1].content)))
    if shield.is_injection(user_msg): return {"messages": [AIMessage(content="Request blocked by security policy.")]}

    intent = state.get("intent", "other")
    sys_prompt = "You are TechZone's support agent. Be concise. Answer ONLY using provided context.\n"

    if intent == "policy": sys_prompt += f"\nContext:\n{await async_search_policy_tool(user_msg)}"
    elif intent == "product": sys_prompt += f"\nCatalog:\n{await async_search_product_tool(user_msg)}"
    elif intent == "greeting": return {"messages": [AIMessage(content="Welcome to TechZone! How can I help?")]}
    
    response = await llm.ainvoke([SystemMessage(content=sys_prompt), *state["messages"]])
    return {"messages": [response]}

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_intent)
    graph.add_node("respond", handle_query)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "respond")
    graph.add_edge("respond", END)
    return graph

async def chat(user_input: str, thread_id: str) -> str:
    os.makedirs("./kb", exist_ok=True)
    async with AsyncSqliteSaver.from_conn_string("./kb/chat_memory.db") as checkpointer:
        app_graph = build_graph().compile(checkpointer=checkpointer)
        result = await app_graph.ainvoke(
            {"messages": [HumanMessage(content=user_input)]}, 
            config={"configurable": {"thread_id": thread_id}}
        )
        return extract_text(result["messages"][-1].content)