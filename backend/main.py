# main.py
# RAG Application ka main entry point
# SQL Server data se RAG pipeline run karta hai

from db_connector import fetch_table_data, get_all_tables, get_table_schema
from data_processor import dataframe_to_documents, chunk_documents, preprocess_dataframe
from vector_store import create_vector_store, load_existing_vector_store, delete_vector_store
from rag_chain import create_rag_chain, ask_question

import os


# ============================================================
# STEP 1: CONFIGURATION — Apni settings yahan set karo
# ============================================================

# Kaunsi table se data lena hai
TABLE_NAME = "products"          # sample.db ki products table

# Kaunse columns text mein jayenge (RAG content)
TEXT_COLUMNS = ["product_name", "category", "description"]

# Kaunse columns metadata mein jayenge (filtering ke liye)
METADATA_COLUMNS = ["id", "price", "stock"]

# Kitne rows fetch karne hain (None = sab)
ROW_LIMIT = 1000

# Naya vector store banana hai ya existing use karna hai
REBUILD_VECTOR_STORE = False   # True = fresh start, False = existing use karo


# ============================================================
# STEP 2: PIPELINE RUN KARO
# ============================================================

def build_rag_pipeline():
    """
    Poora RAG pipeline build karta hai:
    SQL Server → Documents → Embeddings → Vector Store → RAG Chain
    """

    print("=" * 60)
    print("🚀 RAG Pipeline Start Ho Raha Hai")
    print("=" * 60)

    # ------- Vector Store Load ya Build -------
    vector_store = None

    if not REBUILD_VECTOR_STORE:
        vector_store = load_existing_vector_store()

    if vector_store is None or REBUILD_VECTOR_STORE:
        if REBUILD_VECTOR_STORE:
            delete_vector_store()

        # Step 1: SQL Server se data fetch karo
        print(f"\n📦 Step 1: SQL Server se data fetch kar raha hoon...")
        df = fetch_table_data(
            table_name=TABLE_NAME,
            columns=TEXT_COLUMNS + METADATA_COLUMNS,
            limit=ROW_LIMIT
        )
        print(df.head(3))  # Preview

        # Step 2: Data clean karo
        print(f"\n🧹 Step 2: Data clean kar raha hoon...")
        df = preprocess_dataframe(df)

        # Step 3: Documents banao
        print(f"\n📄 Step 3: Documents bana raha hoon...")
        documents = dataframe_to_documents(
            df=df,
            table_name=TABLE_NAME,
            text_columns=TEXT_COLUMNS,
            metadata_columns=METADATA_COLUMNS
        )

        # Step 4: Chunks banao
        print(f"\n✂️ Step 4: Documents chunk kar raha hoon...")
        chunked_docs = chunk_documents(documents, chunk_size=500, chunk_overlap=50)

        # Step 5: Vector store banao
        print(f"\n🔮 Step 5: Vector store bana raha hoon (embeddings)...")
        vector_store = create_vector_store(chunked_docs)

    # Step 6: RAG chain banao
    print(f"\n⛓️ Step 6: RAG chain bana raha hoon...")
    rag_chain = create_rag_chain(vector_store, top_k=4)

    print("\n" + "=" * 60)
    print("✅ RAG Pipeline Ready Hai!")
    print("=" * 60)

    return rag_chain


# ============================================================
# STEP 3: INTERACTIVE Q&A
# ============================================================

def interactive_qa(rag_chain):
    sql_keywords = [
        "kitne", "count", "total", "sum", "average",
        "sabse zyada", "sabse kam", "kitna", "list karo",
        "sabse mehnga", "sabse sasta", "sabse bada", "sabse chhota",
        "sabse mehenga", "sabse mehanga", "sabse mehnga",  # ← spelling variations
        "maximum", "minimum", "highest", "lowest", "most", "least",
        "rank", "top", "bottom",
        "price", "kitni", "cost", "amount", "price kitni", "price kya",
        "jyada", "kam", "se kam", "se jyada", "wale", "under", "above",
        "zyada", "compare", "cheaper", "expensive",
        "mehenga", "mehanga", "sasta",  # ← aur variations
    ]

    print("\n💬 Apna sawaal likho (exit karne ke liye 'quit' likho):\n")

    # Conversation history store karo
    chat_history = []

    while True:
        question = input("Aap: ").strip()

        if not question:
            continue

        if question.lower() in ["quit", "exit", "band karo"]:
            print("👋 Goodbye!")
            break

        # Pichle sawaal ka context add karo
        if chat_history:
            last_qa = chat_history[-1]
            
            # RAG ke liye simple focused question banao
            focus_prompt = f"Pichla jawab: {last_qa['answer']}\nNaya sawaal: {question}"
            
            # SQL ke liye context question
            context_question = f"""
        Pichla sawaal: {last_qa['question']}
        Pichla jawab: {last_qa['answer']}
        Naya sawaal: {question}

        Agar naya sawaal pichle jawab se related hai toh context samjho.
        Warna naya sawaal independently answer karo.
        """
        else:
            focus_prompt = question
            context_question = question

        use_sql = any(keyword in question.lower() for keyword in sql_keywords)

        if use_sql:
            print("🔢 SQL use kar raha hoon...")
            from text_to_sql import answer_with_sql
            answer = answer_with_sql(context_question)
            print(f"\n💬 Jawab: {answer}\n")
        else:
            # RAG ke liye focused question use karo
            result = ask_question(rag_chain, focus_prompt)
            answer = result["answer"]

        # History mein save karo
        chat_history.append({
            "question": question,
            "answer": answer
        })

        print("-" * 50)


# ============================================================
# DEMO MODE — SQL Server ke bina test karo
# ============================================================

def run_demo_mode():
    from vector_store import create_vector_store, delete_vector_store
    from rag_chain import create_rag_chain, ask_question
    from db_connector import fetch_table_data
    from data_processor import dataframe_to_documents, chunk_documents, preprocess_dataframe

    print("=" * 60)
    print("🎮 DEMO MODE — SQLite Data Se Chal Raha Hai")
    print("=" * 60)

    # SQLite se real data lo
    all_docs = []
    tables = {
        "products": {
            "text": ["product_name", "category", "description"],
            "meta": ["id", "price"]
        },
        "customers": {
            "text": ["customer_name", "city", "notes"],
            "meta": ["id", "total_spent"]
        },
        "orders": {
            "text": ["order_id", "customer", "product", "status"],
            "meta": ["id", "amount"]
        },
    }

    for table_name, cols in tables.items():
        try:
            df = fetch_table_data(table_name)
            df = preprocess_dataframe(df)
            docs = dataframe_to_documents(
                df=df,
                table_name=table_name,
                text_columns=cols["text"],
                metadata_columns=cols["meta"]
            )
            all_docs.extend(docs)
        except Exception as e:
            print(f"⚠️ {table_name} table nahi mili: {e}")

    print(f"\n📄 {len(all_docs)} documents bana liye")

    # Vector store banao
    print("\n🔮 Embeddings ban rahe hain...")
    vector_store = create_vector_store(all_docs, collection_name="demo_rag")

    # RAG chain banao
    rag_chain = create_rag_chain(vector_store)

    # Demo sawaal
    demo_questions = [
        "Laptop ki price kya hai?",
        "Yoga Mat ki description kya hai?",
        "Rahul Sharma ne kitna spend kiya?",
    ]

    print("\n" + "=" * 60)
    print("📋 Demo Sawaal Chal Rahe Hain:")
    print("=" * 60)

    for q in demo_questions:
        ask_question(rag_chain, q)
        print()

    # Interactive mode
    print("\n" + "=" * 60)
    print("💬 Ab Apna Sawaal Poochho!")
    print("=" * 60)
    interactive_qa(rag_chain)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    import sys

    # Demo mode check
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo_mode()
    else:
        # Real SQL Server mode
        try:
            rag_chain = build_rag_pipeline()
            interactive_qa(rag_chain)
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\n💡 Tip: Demo mode try karo:")
            print("   python main.py --demo")
