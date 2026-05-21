from django.http import StreamingHttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
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
        time.sleep(0.02)  # Small delay for smooth streaming effect
    
    # Send done signal
    final_chunk = {'type': 'done', 'content': '', 'done': True}
    yield f"data: {json.dumps(final_chunk)}\n\n"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ask_stream(request):
    """Streaming version of regular ask endpoint"""
    import traceback
    
    try:
        question = request.data.get('question', '')
        
        # Import and call regular ask_question to get full answer
        from chat.views import ask_question
        
        # Get full response
        response = ask_question(request)
        answer = response.data.get('answer', '')
        
        # Stream it back word by word
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
        
        # Stream error message
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
        
        # Import and call agent
        from chat.views import ask_agent
        
        # Get full response
        response = ask_agent(request)
        answer = response.data.get('answer', '')
        
        # Stream it back
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