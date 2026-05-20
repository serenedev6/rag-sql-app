# rag_chain.py
import os
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_aws import ChatBedrock  # ← NEW: Import Bedrock
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.documents import Document
from dotenv import load_dotenv
from typing import List

load_dotenv()

ollama_host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
use_groq = os.getenv("USE_GROQ", "false").lower() == "true"
use_bedrock = os.getenv("USE_BEDROCK", "false").lower() == "true"  # ← NEW

def create_rag_chain(vector_store: dict, top_k: int = 4):
    # Choose LLM based on environment variable
    if use_bedrock:
        # Use AWS Bedrock Claude 3.5 Haiku
        llm = ChatBedrock(
             model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0", 
            region_name="us-east-1",
            model_kwargs={
                "temperature": 0,
                "max_tokens": 1000
            }
        )
        print("✅ Using AWS Bedrock (Claude 3.5 Haiku)")
    else:
        # Default to Groq (free and fast)
        llm = ChatGroq(
            api_key=os.getenv("GROQ_API_KEY"),
            model="llama-3.3-70b-versatile",
            temperature=0
        )
        print("✅ Using Groq LLM")

def ask_question(rag_chain: dict, question: str) -> dict:
    from vector_store import search_similar

    print(f"\n🔍 Sawaal: {question}")
    print("⏳ Jawab dhoondh raha hoon...")

    # Similar documents dhundho
    sources = search_similar(rag_chain["vector_store"], question, rag_chain["top_k"])

    # Context banao
    context = "\n\n".join([doc.page_content for doc in sources])

    # LLM se answer lo
    chain = rag_chain["prompt"] | rag_chain["llm"] | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    print(f"\n💬 Jawab: {answer}")

    if sources:
        print(f"\n📚 Sources ({len(sources)} documents use kiye):")
        for i, doc in enumerate(sources, 1):
            table = doc.metadata.get("table", "Unknown")
            print(f"  {i}. Table: {table} | Content: {doc.page_content[:80]}...")

    return {
        "question": question,
        "answer": answer,
        "sources": sources
    }