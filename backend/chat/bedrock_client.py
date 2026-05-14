import boto3
import json
import os

class BedrockClient:
    def __init__(self):
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'  # Bedrock region
        )
        self.model_id = "anthropic.claude-3-5-haiku-20241022-v1:0"
    
    def generate_response(self, prompt, max_tokens=1000):
        """
        Generate a response using Claude 3.5 Haiku via Bedrock
        
        Args:
            prompt (str): The prompt/question
            max_tokens (int): Maximum tokens in response
            
        Returns:
            str: Generated response
        """
        try:
            # Bedrock request body for Claude models
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            # Invoke the model
            response = self.client.invoke_model(
                modelId=self.model_id,
                body=json.dumps(request_body)
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from response
            return response_body['content'][0]['text']
            
        except Exception as e:
            print(f"Bedrock error: {str(e)}")
            raise