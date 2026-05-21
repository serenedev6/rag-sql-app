from django.shortcuts import render
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
import sys
import os
from django.core.cache import cache
import hashlib

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_ask(request):
    print("🎯 TEST ASK ENDPOINT HIT!")
    return Response({'answer': 'Test ask successful!'})

def rate_limit_exceeded(request, exception=None):
    return JsonResponse(
        {
            'error': 'Too many requests. Please try again in a minute.',
            'code': 'rate_limit_exceeded'
        },
        status=429
    )

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
    from data_processor import dataframe_to_documents, preprocess_dataframe
    from db_connector import fetch_table_data

    vector_store = load_existing_vector_store(collection_name="products_rag")

    if vector_store is None:
        print("🔨 Building vector stores...")

        tables = {
            "products": {
                "text": ["product_name", "category", "description"],
                "meta": ["id", "price"],
                "collection": "products_rag"
            },
            "customers": {
                "text": ["customer_name", "city", "notes"],
                "meta": ["id", "total_spent"],
                "collection": "customers_rag"
            },
            "orders": {
                "text": ["order_id", "customer", "product", "status"],
                "meta": ["id", "amount"],
                "collection": "orders_rag"
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
                create_vector_store(docs, collection_name=cols["collection"])
                print(f"✅ {table_name} vector store built with {len(docs)} docs!")
            except Exception as e:
                print(f"⚠️ {table_name} error: {e}")

        vector_store = load_existing_vector_store(collection_name="products_rag")

    return vector_store

# Initialize once at startup
print("🚀 Initializing vector store at startup...")
VECTOR_STORE = initialize_vector_store()
RAG_CHAIN = None

def chat_view(request):
    return render(request, 'chat/index.html')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_question(request):
    import traceback
    
    try:
        print(f"🎯 ASK_QUESTION CALLED! User: {request.user}")
        
        global RAG_CHAIN

        question = request.data.get('question', '')
        answer = ''
        use_sql = False

        # Check cache first
        cache_key = f"answer_{hashlib.md5(question.lower().encode()).hexdigest()}"
        cached_answer = cache.get(cache_key)

        if cached_answer:
            print(f"⚡ cache hit for: {question}")
            return Response({'answer': cached_answer, 'cached': True})

        use_sql = any(keyword in question.lower() for keyword in SQL_KEYWORDS)

        if use_sql:
            print("🔢 SQL mode use kar raha hoon...")
            from text_to_sql import answer_with_sql
            answer = answer_with_sql(question)
        else:
            print("🔍 RAG mode use kar raha hoon...")
            if RAG_CHAIN is None:
                from rag_chain import create_rag_chain
                RAG_CHAIN = create_rag_chain(VECTOR_STORE, top_k=10)
            from rag_chain import ask_question as rag_ask
            from vector_store import search_similar
            similar_docs = search_similar(VECTOR_STORE, question, top_k=10)
            print(f"🔍 Found {len(similar_docs)} similar docs:")
            for doc in similar_docs:
                print(f"  → {doc.page_content[:100]}")
            result = rag_ask(RAG_CHAIN, question)
            answer = result["answer"]

        # Save to cache (10 minutes)
        cache.set(cache_key, answer, timeout=600)
        print(f"💾 Cached answer for: {question}")

        # Save to history
        try:
            from .models import ChatHistory
            ChatHistory.objects.create(
                user=request.user,
                question=question,
                answer=answer,
                mode='sql' if use_sql else 'rag'
            )
        except Exception as e:
            print(f"⚠️ Could not save chat history: {e}")

        return Response({'answer': answer})
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ CHAT ERROR: {error_msg}")
        print(f"🔍 FULL TRACEBACK:")
        traceback.print_exc()
        return Response({'answer': f"Error: {str(e)}"}, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_agent(request):
    import traceback
    
    try:
        print(f"🤖 AGENT MODE! User: {request.user}")
        
        question = request.data.get('question', '')
        
        # Import agent
        from agent import ask_agent as agent_ask
        
        answer = agent_ask(question)
        
        return Response({'answer': answer, 'mode': 'agent'})
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ AGENT ERROR: {error_msg}")
        print(f"🔍 FULL TRACEBACK:")
        traceback.print_exc()
        return Response({'answer': f"Error: {str(e)}"}, status=500)
    


from django.core.files.storage import default_storage
import os

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def upload_and_analyze(request):
    """Upload file and analyze it"""
    import traceback
    
    try:
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=400)
        
        uploaded_file = request.FILES['file']
        question = request.data.get('question', '')
        
        # Save file temporarily
        file_path = default_storage.save(f'uploads/{uploaded_file.name}', uploaded_file)
        full_path = os.path.join(default_storage.location, file_path)
        
        # Process file
        from file_processor import process_file
        file_data = process_file(full_path, question)  # ← Pass question

         # Store file data for agent access
        from agent import UPLOADED_FILE_DATA
        import agent
        agent.UPLOADED_FILE_DATA = file_data  # ← Add this line
        
        # Clean up
        os.remove(full_path)
        
        if 'error' in file_data:
            return Response({'error': file_data['error']}, status=400)
        
        # If question provided, answer it using the file data
        if question:
            from langchain_groq import ChatGroq
            from langchain_core.prompts import ChatPromptTemplate
            from langchain_core.output_parsers import StrOutputParser
            
            llm = ChatGroq(
                api_key=os.getenv("GROQ_API_KEY"),
                model="llama-3.3-70b-versatile",
                temperature=0
            )
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", "You are a helpful assistant analyzing uploaded files."),
                ("human", """File Data:
{file_data}

Question: {question}

Provide a clear, concise answer based on the file data.""")
            ])
            
            chain = prompt | llm | StrOutputParser()
            answer = chain.invoke({
                'file_data': str(file_data),
                'question': question
            })
            
            return Response({
                'file_info': file_data,
                'answer': answer
            })
        else:
            # Just return file info
            return Response({'file_info': file_data})
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ FILE UPLOAD ERROR: {error_msg}")
        traceback.print_exc()
        return Response({'error': error_msg}, status=500)
    


