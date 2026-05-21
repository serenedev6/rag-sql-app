from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import json
import time

def stream_chat_response(answer_text: str):
    """Generator that yields answer word by word"""
    words = answer_text.split()
    
    for i, word in enumerate(words):
        chunk = {
            'type': 'chunk',
            'content': word + (' ' if i < len(words) - 1 else ''),
            'done': False
        }
        yield f"data: {json.dumps(chunk)}\n\n"
        time.sleep(0.02)
    
    final_chunk = {'type': 'done', 'content': '', 'done': True}
    yield f"data: {json.dumps(final_chunk)}\n\n"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_stream(request):
    """Streaming version of regular ask endpoint"""
    import traceback
    
    try:
        question = request.data.get('question', '')
        
        # Call the logic directly, not the view function
        from chat.views import SQL_KEYWORDS, VECTOR_STORE, RAG_CHAIN
        
        use_sql = any(keyword in question.lower() for keyword in SQL_KEYWORDS)
        
        if use_sql:
            print("🔢 SQL mode use kar raha hoon...")
            from text_to_sql import answer_with_sql
            answer = answer_with_sql(question)
        else:
            print("🔍 RAG mode use kar raha hoon...")
            from rag_chain import ask_question as rag_ask, create_rag_chain
            
            global RAG_CHAIN
            if RAG_CHAIN is None:
                RAG_CHAIN = create_rag_chain(VECTOR_STORE, top_k=10)
            
            result = rag_ask(RAG_CHAIN, question)
            answer = result["answer"]
        
        # Stream the answer
        return StreamingHttpResponse(
            stream_chat_response(answer),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ STREAM ERROR: {error_msg}")
        traceback.print_exc()
        
        error_chunk = {'type': 'error', 'content': error_msg, 'done': True}
        return StreamingHttpResponse(
            [f"data: {json.dumps(error_chunk)}\n\n"],
            content_type='text/event-stream'
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_agent_stream(request):
    """Streaming version of agent endpoint"""
    import traceback
    
    try:
        question = request.data.get('question', '')
        
        # Call agent logic directly
        from agent import ask_agent as agent_ask
        answer = agent_ask(question)
        
        # Stream the answer
        return StreamingHttpResponse(
            stream_chat_response(answer),
            content_type='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
            }
        )
        
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(f"❌ AGENT STREAM ERROR: {error_msg}")
        traceback.print_exc()
        
        error_chunk = {'type': 'error', 'content': error_msg, 'done': True}
        return StreamingHttpResponse(
            [f"data: {json.dumps(error_chunk)}\n\n"],
            content_type='text/event-stream'
        )