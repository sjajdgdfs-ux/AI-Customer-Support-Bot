import json
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

from langchain_chroma import Chroma
from langchain_core.documents import Document
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
    {"name": "AirPods Pro 2", "price": 249, "category": "Audio", "availability": "In Stock"},
]


def ensure_data_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_POLICIES)
    if not os.path.exists(PRODUCTS_PATH):
        with open(PRODUCTS_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PRODUCTS, f, indent=2)


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


def get_vector_store():
    qdrant_host = os.getenv("QDRANT_HOST")
    if qdrant_host:
        try:
            from langchain_qdrant import QdrantVectorStore
            from qdrant_client import QdrantClient

            client = QdrantClient(host=qdrant_host, port=int(os.getenv("QDRANT_PORT", "6333")))
            return QdrantVectorStore(
                client=client,
                collection_name="store_policies",
                embedding=get_embeddings()
            )
        except Exception:
            pass  # Fallback to Chroma if Qdrant is unavailable

    import chromadb

    os.makedirs(KB_PATH, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=KB_PATH)
    return Chroma(
        client=chroma_client,
        collection_name="store_policies",
        embedding_function=get_embeddings()
    )


def build_knowledge_base():
    ensure_data_exists()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    # Attach Metadata/Payload to each chunk
    documents = [
        Document(
            page_content=chunk,
            metadata={"source": "policies.md", "type": "store_policy"}
        )
        for chunk in chunks
    ]

    db = get_vector_store()
    db.add_documents(documents)


def search_knowledge(query: str, k: int = 2, filter_metadata: Optional[Dict[str, Any]] = None) -> str:
    ensure_data_exists()
    db = get_vector_store()

    try:
        if filter_metadata:
            results = db.similarity_search(query, k=k, filter=filter_metadata)
        else:
            results = db.similarity_search(query, k=k)

        if not results:
            build_knowledge_base()
            results = db.similarity_search(query, k=k, filter=filter_metadata) if filter_metadata else db.similarity_search(query, k=k)

        return "\n\n".join([doc.page_content for doc in results]) if results else "No info found."
    except Exception:
        build_knowledge_base()
        results = db.similarity_search(query, k=k)
        return "\n\n".join([doc.page_content for doc in results]) if results else "No info found."