import os

PROJECT_NAME = "ecommerce-ai-agent"

FOLDERS = ["app", "data", "kb"]

FILES = {

    ".env": "GOOGLE_API_KEY=your_api_key_here\n",

    "requirements.txt": (
        "langchain>=0.2\n"
        "langchain-google-genai>=1.0\n"
        "langchain-community>=0.2\n"
        "langgraph>=0.2\n"
        "chromadb>=0.5\n"
        "sentence-transformers>=2.2\n"
        "fastapi>=0.111\n"
        "uvicorn>=0.30\n"
        "streamlit>=1.36\n"
        "pydantic>=2.0\n"
        "python-dotenv>=1.0\n"
    ),

    "app/__init__.py": "",

    "data/policies.md": (
        "# TechZone Electronics - Store Policies\n\n"
        "## Shipping Policy\n"
        "- Standard shipping (within city): $5, 1-2 business days\n"
        "- Express shipping (nationwide): $15, 3-5 business days\n"
        "- FREE shipping on orders over $100\n"
        "- Shipping hours: Monday to Saturday, 9 AM - 6 PM\n"
        "- Tracking number sent via email within 24 hours of dispatch\n\n"
        "## Return & Exchange Policy\n"
        "- Returns accepted within 14 days of delivery\n"
        "- Items must be in original condition with packaging and accessories\n"
        "- Free returns for defective or damaged items\n"
        "- Customer covers return shipping for change-of-mind returns\n"
        "- Opened smartphones and laptops are non-returnable unless defective\n"
        "- Refunds processed within 5-7 business days after inspection\n\n"
        "## Warranty Policy\n"
        "- All devices come with 1-year manufacturer warranty\n"
        "- Warranty covers manufacturing defects only\n"
        "- Warranty does NOT cover: water damage, drops, unauthorized repairs\n"
        "- To claim warranty: contact support@techzone.com with order number\n"
        "- Warranty repair turnaround: 7-14 business days\n\n"
        "## Payment Methods\n"
        "- Credit/Debit cards (Visa, Mastercard, Amex)\n"
        "- PayPal\n"
        "- Apple Pay / Google Pay\n"
        "- Buy Now Pay Later: 3-12 month installments via Klarna\n"
        "- Cash on delivery (available for orders under $200)\n\n"
        "## Support Hours\n"
        "- Live chat and email: Daily 8 AM - 11 PM EST\n"
        "- Phone support: Mon-Fri 9 AM - 6 PM EST\n"
        "- Email: support@techzone.com\n"
        "- Phone: +1 (555) 123-4567\n"
    ),

    "data/products.json": (
        '[\n'
        '  {\n'
        '    "name": "iPhone 15 Pro Max 256GB",\n'
        '    "price": 1199,\n'
        '    "category": "Smartphones",\n'
        '    "warranty": "1-year Apple warranty",\n'
        '    "availability": "In Stock",\n'
        '    "colors": ["Natural Titanium", "Blue Titanium", "White Titanium"],\n'
        '    "rating": 4.8\n'
        '  },\n'
        '  {\n'
        '    "name": "Samsung Galaxy S24 Ultra 512GB",\n'
        '    "price": 1419,\n'
        '    "category": "Smartphones",\n'
        '    "warranty": "1-year Samsung warranty",\n'
        '    "availability": "In Stock",\n'
        '    "colors": ["Titanium Black", "Titanium Gray", "Titanium Violet"],\n'
        '    "rating": 4.7\n'
        '  },\n'
        '  {\n'
        '    "name": "MacBook Air M3 15-inch",\n'
        '    "price": 1299,\n'
        '    "category": "Laptops",\n'
        '    "warranty": "1-year Apple warranty",\n'
        '    "availability": "In Stock",\n'
        '    "colors": ["Silver", "Space Gray", "Midnight"],\n'
        '    "rating": 4.9\n'
        '  },\n'
        '  {\n'
        '    "name": "AirPods Pro 2 (USB-C)",\n'
        '    "price": 249,\n'
        '    "category": "Audio",\n'
        '    "warranty": "1-year Apple warranty",\n'
        '    "availability": "In Stock",\n'
        '    "colors": ["White"],\n'
        '    "rating": 4.7\n'
        '  },\n'
        '  {\n'
        '    "name": "iPad Air M2 128GB",\n'
        '    "price": 599,\n'
        '    "category": "Tablets",\n'
        '    "warranty": "1-year Apple warranty",\n'
        '    "availability": "Out of Stock",\n'
        '    "colors": ["Blue", "Purple", "Space Gray"],\n'
        '    "rating": 4.6\n'
        '  }\n'
        ']\n'
    ),

    "app/security.py": (
        "import re\n"
        "\n"
        "\n"
        "class SecurityShield:\n"
        '    """Protects the agent from prompt injection and PII leaks."""\n'
        "\n"
        "    INJECTION_PATTERNS = [\n"
        '        r"ignore\\s+(all\\s+)?(previous|above|prior)",\n'
        '        r"you\\s+are\\s+now",\n'
        '        r"system\\s*prompt",\n'
        '        r"forget\\s+(everything|all)",\n'
        '        r"new\\s+instructions?",\n'
        '        r"do\\s+not\\s+follow",\n'
        '        r"disregard\\s+(all|previous|your)",\n'
        '        r"override\\s+(your|the)\\s+(instructions?|rules?)",\n'
        '        r"act\\s+as\\s+(if|a)\\s+(different|new)",\n'
        "    ]\n"
        "\n"
        "    PII_PATTERNS = {\n"
        '        "email": r"\\b[\\w.+-]+@[\\w-]+\\.[\\w.]+\\b",\n'
        '        "phone": r"\\b\\+?1?\\s*\\(?\\d{3}\\)?[\\s.-]?\\d{3}[\\s.-]?\\d{4}\\b",\n'
        '        "ssn": r"\\b\\d{3}-\\d{2}-\\d{4}\\b",\n'
        '        "credit_card": r"\\b\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}[\\s-]?\\d{4}\\b",\n'
        "    }\n"
        "\n"
        "    def is_injection(self, text: str) -> bool:\n"
        '        """Check if the input contains prompt injection attempts."""\n'
        "        text_lower = text.lower()\n"
        "        return any(\n"
        "            re.search(pattern, text_lower)\n"
        "            for pattern in self.INJECTION_PATTERNS\n"
        "        )\n"
        "\n"
        "    def redact_pii(self, text: str) -> str:\n"
        '        """Remove PII before sending to LLM."""\n'
        "        for pii_type, pattern in self.PII_PATTERNS.items():\n"
        '            text = re.sub(pattern, f"[REDACTED_{pii_type.upper()}]", text)\n'
        "        return text\n"
    ),

    "app/rag.py": (
        "import os\n"
        "from langchain_community.embeddings import HuggingFaceEmbeddings\n"
        "from langchain_community.vectorstores import Chroma\n"
        "from langchain.text_splitter import RecursiveCharacterTextSplitter\n"
        "\n"
        'KB_PATH = "./kb"\n'
        'DATA_PATH = "./data/policies.md"\n'
        "\n"
        "\n"
        "def get_embeddings():\n"
        "    return HuggingFaceEmbeddings(\n"
        '        model_name="all-MiniLM-L6-v2",\n'
        '        model_kwargs={"device": "cpu"}\n'
        "    )\n"
        "\n"
        "\n"
        "def build_knowledge_base():\n"
        '    """Chunk and store policies into ChromaDB."""\n'
        '    with open(DATA_PATH, "r", encoding="utf-8") as f:\n'
        "        text = f.read()\n"
        "\n"
        "    splitter = RecursiveCharacterTextSplitter(\n"
        "        chunk_size=500,\n"
        "        chunk_overlap=50,\n"
        '        separators=["\\n## ", "\\n### ", "\\n- ", "\\n\\n"]\n'
        "    )\n"
        "    chunks = splitter.split_text(text)\n"
        "\n"
        "    embeddings = get_embeddings()\n"
        "    Chroma.from_texts(\n"
        "        texts=chunks,\n"
        "        embedding=embeddings,\n"
        "        persist_directory=KB_PATH,\n"
        '        collection_name="store_policies"\n'
        "    )\n"
        '    print(f"Stored {len(chunks)} chunks in knowledge base")\n'
        "\n"
        "\n"
        "def search_knowledge(query: str, k: int = 3) -> str:\n"
        '    """Retrieve relevant policy documents."""\n'
        "    if not os.path.exists(KB_PATH):\n"
        "        build_knowledge_base()\n"
        "\n"
        "    embeddings = get_embeddings()\n"
        "    db = Chroma(\n"
        "        persist_directory=KB_PATH,\n"
        "        embedding_function=embeddings,\n"
        '        collection_name="store_policies"\n'
        "    )\n"
        "\n"
        "    results = db.similarity_search(query, k=k)\n"
        "    if not results:\n"
        '        return "No relevant information found."\n'
        "\n"
        '    return "\\n\\n".join([doc.page_content for doc in results])\n'
    ),

    "app/agent.py": (
        "import json\n"
        "from typing import TypedDict, Annotated\n"
        "from langgraph.graph import StateGraph, START, END\n"
        "from langgraph.graph.message import add_messages\n"
        "from langchain_google_genai import ChatGoogleGenerativeAI\n"
        "from langchain_core.messages import SystemMessage, HumanMessage, AIMessage\n"
        "\n"
        "from app.rag import search_knowledge\n"
        "from app.security import SecurityShield\n"
        "\n"
        "\n"
        "class AgentState(TypedDict):\n"
        "    messages: Annotated[list, add_messages]\n"
        "    intent: str\n"
        "\n"
        "\n"
        "def search_policy_tool(query: str) -> str:\n"
        '    """Search the store policy knowledge base."""\n'
        "    return search_knowledge(query)\n"
        "\n"
        "\n"
        "def search_product_tool(product_name: str) -> str:\n"
        '    """Search the product catalog."""\n'
        '    with open("./data/products.json", "r", encoding="utf-8") as f:\n'
        "        products = json.load(f)\n"
        "\n"
        "    results = [\n"
        "        p for p in products\n"
        '        if product_name.lower() in p["name"].lower()\n'
        '        or product_name.lower() in p["category"].lower()\n'
        "    ]\n"
        "\n"
        "    if not results:\n"
        "        return f\"No product found matching '{product_name}'.\"\n"
        '    return json.dumps(results, ensure_ascii=False, indent=2)\n'
        "\n"
        "\n"
        "llm = ChatGoogleGenerativeAI(\n"
        '    model="gemini-2.0-flash",\n'
        "    temperature=0.3\n"
        ")\n"
        "\n"
        "shield = SecurityShield()\n"
        "\n"
        "\n"
        "def classify_intent(state: AgentState) -> AgentState:\n"
        '    """Classify user intent."""\n'
        '    user_msg = state["messages"][-1].content\n'
        "\n"
        "    prompt = (\n"
        '        "Classify this customer message into exactly ONE category:\\n"\n'
        '        "- policy (shipping, returns, warranty, payment)\\n"\n'
        '        "- product (product info, pricing, availability)\\n"\n'
        '        "- greeting (hello, hi, hey, thanks)\\n"\n'
        '        "- complaint (angry customer, negative experience)\\n"\n'
        '        "- other (anything else)\\n\\n"\n'
        "        f\"Customer message: {user_msg}\\n\\n\"\n"
        '        "Reply with ONLY the category word."\n'
        "    )\n"
        "\n"
        "    response = llm.invoke([HumanMessage(content=prompt)])\n"
        '    intent = response.content.strip().lower()\n'
        '    return {"intent": intent}\n'
        "\n"
        "\n"
        "def handle_query(state: AgentState) -> AgentState:\n"
        '    """Generate response based on intent."""\n'
        '    user_msg = state["messages"][-1].content\n'
        '    intent = state.get("intent", "other")\n'
        "\n"
        "    if shield.is_injection(user_msg):\n"
        '        return {"messages": [AIMessage(\n'
        '            content="I didn\'t quite understand that. Could you rephrase?"\n'
        "        )]}\n"
        "\n"
        "    system_prompt = (\n"
        "        \"You are a friendly customer support agent for TechZone Electronics.\\n\"\n"
        "        \"RULES:\\n\"\n"
        "        \"- Be concise, warm, and helpful\\n\"\n"
        "        \"- Use simple English\\n\"\n"
        "        \"- If unsure, say: Let me connect you with a human agent.\\n\"\n"
        "        \"- NEVER make up information\\n\"\n"
        "        \"- For complaints: empathize first, then offer solutions\\n\"\n"
        "        \"- Always end with: Is there anything else I can help you with?\\n\"\n"
        "    )\n"
        "\n"
        '    if intent == "policy":\n'
        "        context = search_policy_tool(user_msg)\n"
        '        system_prompt += f"\\n\\nRelevant policies:\\n{context}"\n'
        "\n"
        '    elif intent == "product":\n'
        "        context = search_product_tool(user_msg)\n"
        '        system_prompt += f"\\n\\nProduct data:\\n{context}"\n'
        "\n"
        '    elif intent == "greeting":\n'
        '        return {"messages": [AIMessage(\n'
        '            content="Welcome to TechZone Electronics! How can I help you today?"\n'
        "        )]}\n"
        "\n"
        '    elif intent == "complaint":\n'
        "        system_prompt += (\n"
        '            "\\n\\nCOMPLAINT PROTOCOL:\\n"\n'
        '            "1. Acknowledge frustration\\n"\n'
        '            "2. Apologize\\n"\n'
        '            "3. Offer a solution\\n"\n'
        '            "4. Provide human support contact\\n"\n'
        "        )\n"
        "\n"
        "    messages = [\n"
        "        SystemMessage(content=system_prompt),\n"
        '        *state["messages"]\n'
        "    ]\n"
        "\n"
        "    response = llm.invoke(messages)\n"
        '    return {"messages": [response]}\n'
        "\n"
        "\n"
        "def build_agent():\n"
        "    graph = StateGraph(AgentState)\n"
        '    graph.add_node("classify", classify_intent)\n'
        '    graph.add_node("respond", handle_query)\n'
        '    graph.add_edge(START, "classify")\n'
        '    graph.add_edge("classify", "respond")\n'
        '    graph.add_edge("respond", END)\n'
        "    return graph.compile()\n"
        "\n"
        "\n"
        "agent = build_agent()\n"
        "\n"
        "\n"
        "async def chat(user_input: str, history: list = None) -> str:\n"
        '    """Main chat function."""\n'
        "    messages = history or []\n"
        "    messages.append(HumanMessage(content=user_input))\n"
        '    result = await agent.ainvoke({"messages": messages})\n'
        '    return result["messages"][-1].content\n'
    ),

    "app/models.py": (
        "from pydantic import BaseModel\n"
        "from typing import Optional\n"
        "\n"
        "\n"
        "class ChatRequest(BaseModel):\n"
        "    message: str\n"
        '    thread_id: Optional[str] = "default"\n'
        "\n"
        "\n"
        "class ChatResponse(BaseModel):\n"
        "    reply: str\n"
        "    intent: str\n"
        "    thread_id: str\n"
    ),

    "build_kb.py": (
        "from app.rag import build_knowledge_base\n"
        "\n"
        'if __name__ == "__main__":\n'
        '    print("Building knowledge base...")\n'
        "    build_knowledge_base()\n"
        '    print("Done!")\n'
    ),

    "main.py": (
        "from fastapi import FastAPI\n"
        "from fastapi.middleware.cors import CORSMiddleware\n"
        "from app.agent import chat\n"
        "from app.models import ChatRequest, ChatResponse\n"
        "\n"
        'app = FastAPI(title="TechZone AI Support Agent")\n'
        "\n"
        "app.add_middleware(\n"
        "    CORSMiddleware,\n"
        '    allow_origins=["*"],\n'
        '    allow_methods=["*"],\n'
        '    allow_headers=["*"],\n'
        ")\n"
        "\n"
        "\n"
        '@app.post("/chat", response_model=ChatResponse)\n'
        "async def chat_endpoint(request: ChatRequest):\n"
        "    reply = await chat(request.message)\n"
        "    return ChatResponse(\n"
        "        reply=reply,\n"
        '        intent="classified",\n'
        "        thread_id=request.thread_id\n"
        "    )\n"
        "\n"
        "\n"
        '@app.get("/health")\n'
        "async def health():\n"
        '    return {"status": "ok", "agent": "TechZone AI v1.0"}\n'
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    import uvicorn\n"
        '    uvicorn.run(app, host="0.0.0.0", port=8000)\n'
    ),

    "ui.py": (
        "import streamlit as st\n"
        "import asyncio\n"
        "from app.agent import chat\n"
        "\n"
        "st.set_page_config(\n"
        '    page_title="TechZone AI Support",\n'
        '    page_icon="🛒",\n'
        '    layout="centered"\n'
        ")\n"
        "\n"
        'st.title("🛒 TechZone AI Support")\n'
        'st.caption("Ask about products, shipping, returns, or warranties!")\n'
        "\n"
        'if "messages" not in st.session_state:\n'
        '    st.session_state.messages = []\n'
        "\n"
        'for msg in st.session_state.messages:\n'
        '    with st.chat_message(msg["role"]):\n'
        '        st.markdown(msg["content"])\n'
        "\n"
        'if prompt := st.chat_input("Type your question here..."):\n'
        '    st.session_state.messages.append({"role": "user", "content": prompt})\n'
        '    with st.chat_message("user"):\n'
        "        st.markdown(prompt)\n"
        "\n"
        '    with st.chat_message("assistant"):\n'
        '        with st.spinner("Thinking..."):\n'
        "            reply = asyncio.run(chat(prompt))\n"
        "        st.markdown(reply)\n"
        "\n"
        '    st.session_state.messages.append({"role": "assistant", "content": reply})\n'
    ),

    "README.md": (
        "# TechZone AI Customer Support Agent\n\n"
        "An intelligent AI customer support bot built with LangGraph, Gemini 2.0, RAG, and FastAPI.\n\n"
        "## Features\n\n"
        "- Intent Classification (policy, product, complaint, greeting)\n"
        "- RAG-Powered Answers from ChromaDB\n"
        "- Security Shield (prompt injection + PII redaction)\n"
        "- Async FastAPI Backend\n"
        "- Streamlit Chat UI\n\n"
        "## Quick Start\n\n"
        "    pip install -r requirements.txt\n"
        "    # Edit .env with your API key\n"
        "    python build_kb.py\n"
        "    streamlit run ui.py\n\n"
        "## Tech Stack\n\n"
        "| Layer | Technology |\n"
        "|-------|------------|\n"
        "| LLM | Gemini 2.0 Flash |\n"
        "| Orchestration | LangGraph |\n"
        "| RAG | LangChain + ChromaDB |\n"
        "| Backend | FastAPI |\n"
        "| Frontend | Streamlit |\n"
    ),

    ".gitignore": (
        "__pycache__/\n"
        "*.pyc\n"
        ".env\n"
        "kb/\n"
        ".venv/\n"
        "venv/\n"
        "*.egg-info/\n"
        ".DS_Store\n"
    ),
}


def main():
    print("=" * 50)
    print("  TechZone AI Agent - Project Setup")
    print("=" * 50)

    os.makedirs(PROJECT_NAME, exist_ok=True)
    os.chdir(PROJECT_NAME)
    print(f"\nCreated: {PROJECT_NAME}/")

    for folder in FOLDERS:
        os.makedirs(folder, exist_ok=True)
        print(f"  [folder] {folder}/")

    print(f"\nCreating {len(FILES)} files...")
    for filepath, content in FILES.items():
        parent = os.path.dirname(filepath)
        if parent:
            os.makedirs(parent, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  [file] {filepath}")

    print("\n" + "=" * 50)
    print("  DONE!")
    print("=" * 50)
    print(f"""
  Next steps:
    cd {PROJECT_NAME}
    pip install -r requirements.txt
    # Edit .env -> add your real API key
    python build_kb.py
    streamlit run ui.py
""")


if __name__ == "__main__":
    main()