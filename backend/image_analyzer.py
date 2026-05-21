import base64
from typing import Dict, Any
import os
from dotenv import load_dotenv

load_dotenv()

def encode_image_to_base64(image_path: str) -> str:
    """Convert image to base64"""
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image_with_claude(image_path: str, question: str = "What's in this image?") -> Dict[str, Any]:
    """Analyze image using Claude Sonnet with vision"""
    try:
        from anthropic import AnthropicBedrock
        
        # Initialize Bedrock client
        client = AnthropicBedrock(
            aws_region="us-east-1"
        )
        
        # Get image extension
        ext = os.path.splitext(image_path)[1].lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')
        
        # Encode image
        image_data = encode_image_to_base64(image_path)
        
        # Call Claude with vision
        message = client.messages.create(
            model="anthropic.claude-3-5-sonnet-20241022-v2:0",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ],
                }
            ],
        )
        
        # Extract text response
        answer = message.content[0].text
        
        return {
            'success': True,
            'answer': answer,
            'model': 'claude-sonnet-3.5'
        }
        
    except Exception as e:
        print(f"❌ Vision error: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def analyze_image_with_groq(image_path: str, question: str = "What's in this image?") -> Dict[str, Any]:
    """Fallback: Use Groq with LLaVA (if Bedrock fails)"""
    try:
        # Groq doesn't support vision yet, return error
        return {
            'success': False,
            'error': 'Groq does not support vision. Please use Bedrock.'
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def analyze_image(image_path: str, question: str = "What's in this image?", use_bedrock: bool = True) -> Dict[str, Any]:
    """Main entry point for image analysis"""
    
    if use_bedrock:
        return analyze_image_with_claude(image_path, question)
    else:
        return analyze_image_with_groq(image_path, question)