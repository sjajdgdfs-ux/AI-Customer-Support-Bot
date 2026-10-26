import os
import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 📍 مسارات مطلقة ديناميكية
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
KB_PATH = os.path.join(BASE_DIR, "kb")
DATA_PATH = os.path.join(DATA_DIR, "policies.md")
PRODUCTS_PATH = os.path.join(DATA_DIR, "products.json")

# 📝 بيانات احتياطية تُنشأ أوتوماتيكياً في حالة عدم وجود الملفات على الكلاود
DEFAULT_POLICIES = """# TechZone Electronics — Store Policies

## Shipping Policy
- Standard shipping: $5, 1-2 business days
- Express shipping: $15, 3-5 business days
- FREE shipping on orders over $100

## Return Policy
- Returns accepted within 14 days of delivery
- Items must be in original condition with packaging
- Free returns for defective or damaged items

## Warranty Policy
- All devices come with 1-year manufacturer warranty
- Warranty covers manufacturing defects only

## Support Hours
- Live support: Daily 8 AM - 11 PM EST
- Email: support@techzone.com
"""

DEFAULT_PRODUCTS = [
  {"name": "iPhone 15 Pro Max 256GB", "price": 1199, "category": "Smartphones", "warranty": "1-year Apple warranty", "availability": "In Stock"},
  {"name": "Samsung Galaxy S24 Ultra", "price": 1419, "category": "Smartphones", "warranty": "1-year Samsung warranty", "availability": "In Stock"},
  {"name": "MacBook Air M3 15-inch", "price": 1299, "category": "Laptops", "warranty": "1-year Apple warranty", "availability": "In Stock"},
  {"name": "AirPods Pro 2", "price": 249, "category": "Audio", "warranty": "1-year Apple warranty", "availability": "In Stock"}
]


def ensure_data_exists():
    """إنشاء المجلد والملفات تلقائياً لو مش موجودة على الكلاود"""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            f.write(DEFAULT_POLICIES)
    if not os.path.exists(PRODUCTS_PATH):
        with open(PRODUCTS_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_PRODUCTS, f, indent=2)


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


def build_knowledge_base():
    ensure_data_exists()
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)

    embeddings = get_embeddings()
    Chroma.from_texts(
        texts=chunks,
        embedding=embeddings,
        persist_directory=KB_PATH,
        collection_name="store_policies"
    )
    print(f"Stored {len(chunks)} chunks in knowledge base")


def search_knowledge(query: str, k: int = 3) -> str:
    if not os.path.exists(KB_PATH):
        build_knowledge_base()

    embeddings = get_embeddings()
    db = Chroma(
        persist_directory=KB_PATH,
        embedding_function=embeddings,
        collection_name="store_policies"
    )

    results = db.similarity_search(query, k=k)
    if not results:
        return "No relevant information found."

    return "\n\n".join([doc.page_content for doc in results])