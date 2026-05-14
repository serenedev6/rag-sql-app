from langchain_aws import ChatBedrock

def test_bedrock():
    """Test Bedrock directly without vector store"""
    try:
        llm = ChatBedrock(
            model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
            region_name="us-east-1",
            model_kwargs={
                "temperature": 0,
                "max_tokens": 1000
            }
        )
        
        response = llm.invoke("Hello! Can you introduce yourself in one sentence?")
        return {"success": True, "response": response.content}
    except Exception as e:
        return {"success": False, "error": str(e)}