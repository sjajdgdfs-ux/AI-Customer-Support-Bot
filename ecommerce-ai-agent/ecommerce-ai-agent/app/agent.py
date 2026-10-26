import json
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.rag import search_knowledge
from app.security import SecurityShield


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    intent: str


def search_policy_tool(query: str) -> str:
    """Search the store policy knowledge base."""
    return search_knowledge(query)


def search_product_tool(product_name: str) -> str:
    """Search the product catalog."""
    with open("./data/products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    results = [
        p for p in products
        if product_name.lower() in p["name"].lower()
        or product_name.lower() in p["category"].lower()
    ]

    if not results:
        return f"No product found matching '{product_name}'."
    return json.dumps(results, ensure_ascii=False, indent=2)


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.3
)

shield = SecurityShield()


def classify_intent(state: AgentState) -> AgentState:
    """Classify user intent."""
    user_msg = state["messages"][-1].content

    prompt = (
        "Classify this customer message into exactly ONE category:\n"
        "- policy (shipping, returns, warranty, payment)\n"
        "- product (product info, pricing, availability)\n"
        "- greeting (hello, hi, hey, thanks)\n"
        "- complaint (angry customer, negative experience)\n"
        "- other (anything else)\n\n"
        f"Customer message: {user_msg}\n\n"
        "Reply with ONLY the category word."
    )

    response = llm.invoke([HumanMessage(content=prompt)])
    intent = response.content.strip().lower()
    return {"intent": intent}


def handle_query(state: AgentState) -> AgentState:
    """Generate response based on intent."""
    user_msg = state["messages"][-1].content
    intent = state.get("intent", "other")

    if shield.is_injection(user_msg):
        return {"messages": [AIMessage(
            content="I didn't quite understand that. Could you rephrase?"
        )]}

    system_prompt = (
        "You are a friendly customer support agent for TechZone Electronics.\n"
        "RULES:\n"
        "- Be concise, warm, and helpful\n"
        "- Use simple English\n"
        "- If unsure, say: Let me connect you with a human agent.\n"
        "- NEVER make up information\n"
        "- For complaints: empathize first, then offer solutions\n"
        "- Always end with: Is there anything else I can help you with?\n"
    )

    if intent == "policy":
        context = search_policy_tool(user_msg)
        system_prompt += f"\n\nRelevant policies:\n{context}"

    elif intent == "product":
        context = search_product_tool(user_msg)
        system_prompt += f"\n\nProduct data:\n{context}"

    elif intent == "greeting":
        return {"messages": [AIMessage(
            content="Welcome to TechZone Electronics! How can I help you today?"
        )]}

    elif intent == "complaint":
        system_prompt += (
            "\n\nCOMPLAINT PROTOCOL:\n"
            "1. Acknowledge frustration\n"
            "2. Apologize\n"
            "3. Offer a solution\n"
            "4. Provide human support contact\n"
        )

    messages = [
        SystemMessage(content=system_prompt),
        *state["messages"]
    ]

    response = llm.invoke(messages)
    return {"messages": [response]}


def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("classify", classify_intent)
    graph.add_node("respond", handle_query)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "respond")
    graph.add_edge("respond", END)
    return graph.compile()


agent = build_agent()


async def chat(user_input: str, history: list = None) -> str:
    """Main chat function."""
    messages = history or []
    messages.append(HumanMessage(content=user_input))
    result = await agent.ainvoke({"messages": messages})
    return result["messages"][-1].content
