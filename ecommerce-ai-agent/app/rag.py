import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

KB_PATH = "./kb"
DATA_PATH = "./data/policies.md"

def get_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"})

def build_knowledge_base():
    with open(DATA_PATH, "r", encoding="utf-8") as f: text = f.read()
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_text(text)
    Chroma.from_texts(texts=chunks, embedding=get_embeddings(), persist_directory=KB_PATH, collection_name="store_policies")

def search_knowledge(query: str, k: int = 3) -> str:
    if not os.path.exists(KB_PATH): build_knowledge_base()
    db = Chroma(persist_directory=KB_PATH, embedding_function=get_embeddings(), collection_name="store_policies")
    results = db.similarity_search(query, k=k)
    return "\n\n".join([doc.page_content for doc in results]) if results else "No info found."