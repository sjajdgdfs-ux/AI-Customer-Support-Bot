import os
import json
import chromadb
from functools import lru_cache
try:
    from langchain_chroma import Chroma
except ImportError:
    from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KB_PATH = os.path.join(BASE_DIR, "kb")
DATA_PATH = os.path.join(DATA_DIR, "policies.md")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")

DEFAULT_POLICIES = """# TechZone Electronics — Store Policies
## Shipping Policy
- Standard shipping: $5, 1-2 business days
- Express shipping: $15, 3-5 business days
- FREE shipping on orders over $100

## Return Policy
- Returns accepted within 14 days of delivery
- Free returns for defective items

## Warranty Policy
- 1-year manufacturer warranty on all devices
"""

DEFAULT_PRODUCTS = [
  {"name": "iPhone 15 Pro Max 256GB", "price": 1199, "category": "Smartphones", "availability": "In Stock"},
  {"name": "Samsung Galaxy S24 Ultra", "price": 1419, "category": "Smartphones", "availability": "In Stock"},
  {"name": "MacBook Air M3 15-inch", "price": 1299, "category": "Laptops", "availability": "In Stock"},
  {"name": "AirPods Pro 2", "price": 249, "category": "Audio", "availability": "In Stock"}
]

def ensure_data_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f: f.write(DEFAULT_POLICIES)
    if not os.path.exists(PRODUCTS_PATH):
        with open(PRODUCTS_PATH, "w", encoding="utf-8") as f: json.dump(DEFAULT_PRODUCTS, f, indent=2)

# ⚡ Caching embeddings model so it stays in memory (Instant loading)
@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )

@lru_cache(maxsize=1)
def get_chroma_client():
    os.makedirs(KB_PATH, exist_ok=True)
    return chromadb.PersistentClient(path=KB_PATH)

def get_vector_store():
    return Chroma(
        client=get_chroma_client(),
        collection_name="store_policies",
        embedding_function=get_embeddings()
    )

def build_knowledge_base():
    ensure_data_exists()
    with open(DATA_PATH, "r", encoding="utf-8") as f: text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    db = get_vector_store()
    db.add_texts(texts=chunks)

def search_knowledge(query: str, k: int = 2) -> str:
    db = get_vector_store()
    if len(db.get().get("ids", [])) == 0:
        build_knowledge_base()
    results = db.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results]) if results else "No info found."