# vector_store.py
import os
import chromadb
from langchain_core.documents import Document
from typing import List

llama_host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
use_groq = os.getenv("USE_GROQ", "false").lower() == "true"

CHROMA_DB_PATH = "./chroma_db"


def get_embeddings_model():
    if use_groq:
        # Use chromadb default embeddings (no extra packages needed)
        print("✅ Using ChromaDB default embeddings")
        return None
    else:
        from langchain_ollama import OllamaEmbeddings
        print(f"🔗 Ollama URL: {llama_host}")
        return OllamaEmbeddings(model="nomic-embed-text", base_url=llama_host)


def create_vector_store(documents: List[Document], collection_name: str = "sql_rag"):
    print(f"⏳ {len(documents)} documents ke embeddings ban rahe hain...")

    embeddings_model = get_embeddings_model()

    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)

    try:
        client.delete_collection(collection_name)
    except:
        pass

    collection = client.create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    if embeddings_model is None:
        # ChromaDB handles embeddings internally
        print("🔄 ChromaDB embeddings generate ho rahi hain...")
        collection.add(
            documents=texts,
            ids=[f"doc_{i}" for i in range(len(texts))],
            metadatas=metadatas
        )
    else:
        # Use Ollama embeddings
        print("🔄 Ollama embeddings generate ho rahi hain...")
        embeddings = embeddings_model.embed_documents(texts)
        print(f"✅ {len(embeddings)} embeddings bani — size: {len(embeddings[0])}")
        collection.add(
            embeddings=embeddings,
            documents=texts,
            ids=[f"doc_{i}" for i in range(len(texts))],
            metadatas=metadatas
        )

    print(f"✅ Vector store ready! {len(texts)} documents store kiye")

    return {
        "collection": collection,
        "embeddings_model": embeddings_model,
        "client": client,
        "collection_name": collection_name
    }


def load_existing_vector_store(collection_name: str = "sql_rag"):
    if not os.path.exists(CHROMA_DB_PATH):
        print("⚠️ Koi existing vector store nahi mila")
        return None

    try:
        embeddings_model = get_embeddings_model()
        client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        collection = client.get_collection(collection_name)

        print("✅ Existing vector store load ho gaya!")
        return {
            "collection": collection,
            "embeddings_model": embeddings_model,
            "client": client,
            "collection_name": collection_name
        }
    except Exception as e:
        print(f"⚠️ Load failed: {e}")
        return None


def delete_vector_store():
    import shutil
    if os.path.exists(CHROMA_DB_PATH):
        shutil.rmtree(CHROMA_DB_PATH)
        print("✅ Vector store delete ho gaya")
    else:
        print("⚠️ Koi vector store nahi mila")


def search_similar(vector_store: dict, query: str, top_k: int = 4) -> List[Document]:
    collection = vector_store["collection"]
    embeddings_model = vector_store["embeddings_model"]

    if embeddings_model is None:
        # ChromaDB handles query embeddings internally
        results = collection.query(
            query_texts=[query],
            n_results=top_k
        )
    else:
        query_embedding = embeddings_model.embed_query(query)
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

    docs = []
    for i, text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i] if results["metadatas"] else {}
        docs.append(Document(page_content=text, metadata=metadata))

    return docs