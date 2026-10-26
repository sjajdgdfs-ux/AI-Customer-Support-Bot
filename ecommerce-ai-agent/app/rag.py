import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

# 📍 مسار ديناميكي مطلق يعمل على أي سيرفر أو جهاز محلي
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_PATH = os.path.join(BASE_DIR, "kb")
DATA_PATH = os.path.join(BASE_DIR, "data", "policies.md")


def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={"device": "cpu"}
    )


def build_knowledge_base():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Missing policies file at: {DATA_PATH}")

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