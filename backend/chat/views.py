from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

SQL_KEYWORDS = [
    # Hinglish
    "kitne", "count", "total", "sum", "average",
    "sabse zyada", "sabse kam", "kitna", "list karo",
    "sabse mehnga", "sabse sasta", "sabse bada", "sabse chhota",
    "sabse mehenga", "sabse mehanga",
    "maximum", "minimum", "highest", "lowest", "most", "least",
    "rank", "top", "bottom", "price", "kitni", "cost", "amount",
    "jyada", "kam", "se kam", "se jyada", "wale", "under", "above",
    "zyada", "compare", "cheaper", "expensive", "mehenga", "sasta",
    # English
    "most expensive", "cheapest", "highest price", "lowest price",
    "how many", "how much", "what is the price", "what is the cost",
    "order by", "sort by", "ranked", "top 5", "top 10",
    "more than", "less than", "greater than", "between",
    "avg", "max", "min", "best price", "worst price",
    "affordable", "costly", "budget", "premium",
    "list all", "show all", "get all", "fetch all",
]

# ============================================================
# Initialize vector store ONCE when Django starts
# ============================================================
def initialize_vector_store():
    from vector_store import load_existing_vector_store, create_vector_store
    from data_processor import dataframe_to_documents, chunk_documents, preprocess_dataframe
    from db_connector import fetch_table_data

    vector_store = load_existing_vector_store(collection_name="demo_rag")

    if vector_store is None:
        print("🔨 Building vector store...")
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
                print(f"⚠️ {table_name} table error: {e}")

        vector_store = create_vector_store(all_docs, collection_name="demo_rag")
        print(f"✅ Vector store built with {len(all_docs)} docs!")

    return vector_store

# Initialize once at startup
print("🚀 Initializing vector store at startup...")
VECTOR_STORE = initialize_vector_store()
RAG_CHAIN = None

def chat_view(request):
    return render(request, 'chat/index.html')

@csrf_exempt
def ask_question(request):
    global RAG_CHAIN

    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('question', '')

        try:
            # Decide SQL or RAG mode
            use_sql = any(keyword in question.lower() for keyword in SQL_KEYWORDS)

            if use_sql:
                print("🔢 SQL mode use kar raha hoon...")
                from text_to_sql import answer_with_sql
                answer = answer_with_sql(question)
            else:
                print("🔍 RAG mode use kar raha hoon...")
                if RAG_CHAIN is None:
                    from rag_chain import create_rag_chain
                    RAG_CHAIN = create_rag_chain(VECTOR_STORE)
                from rag_chain import ask_question as rag_ask
                from vector_store import search_similar
                # Debug: see what documents are found
                similar_docs = search_similar(VECTOR_STORE, question, top_k=4)
                print(f"🔍 Found {len(similar_docs)} similar docs:")
                for doc in similar_docs:
                    print(f"  → {doc.page_content[:100]}")
                result = rag_ask(RAG_CHAIN, question)
                answer = result["answer"]

        except Exception as e:
            answer = f"Error: {str(e)}"

        return JsonResponse({'answer': answer})

    return JsonResponse({'error': 'Invalid request'}, status=400)