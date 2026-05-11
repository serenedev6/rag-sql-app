import boto3
import json
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, username, otp):
    """
    Send OTP email via AWS Lambda
    """
    try:
        # Create Lambda client
        lambda_client = boto3.client('lambda', region_name='us-east-2')
        
        # Prepare payload
        payload = {
            'email': email,
            'username': username,
            'otp': otp
        }
        
        # Invoke Lambda function asynchronously (don't wait for response)
        response = lambda_client.invoke(
            FunctionName='send-otp-email',
            InvocationType='Event',  # Async invocation
            Payload=json.dumps(payload)
        )
        
        logger.info(f"Lambda invoked for {email}, StatusCode: {response['StatusCode']}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to invoke Lambda: {str(e)}")
        return False