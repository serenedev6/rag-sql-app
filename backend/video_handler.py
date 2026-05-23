import boto3
from botocore.config import Config
import os
from datetime import datetime

# Initialize S3 client
s3_client = boto3.client(
    's3',
    region_name=os.getenv('AWS_REGION', 'us-east-2'),
    config=Config(signature_version='s3v4')
)

BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'sm-frontend-videos')

def generate_presigned_upload_url(user_id: int, filename: str, content_type: str) -> dict:
    """Generate a pre-signed URL for uploading video to S3"""
    
    # Create unique S3 key
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_key = f"videos/{user_id}/{timestamp}_{filename}"
    
    # Generate pre-signed URL (valid for 10 minutes)
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': s3_key,
            'ContentType': content_type
        },
        ExpiresIn=600  # 10 minutes
    )
    
    return {
        'upload_url': presigned_url,
        's3_key': s3_key,
        's3_url': f"https://{BUCKET_NAME}.s3.{os.getenv('AWS_REGION', 'us-east-2')}.amazonaws.com/{s3_key}"
    }

def generate_presigned_view_url(s3_key: str, expires_in: int = 3600) -> str:
    """Generate a pre-signed URL for viewing/downloading video"""
    
    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': BUCKET_NAME,
            'Key': s3_key
        },
        ExpiresIn=expires_in  # Default 1 hour
    )
    
    return presigned_url

def delete_video_from_s3(s3_key: str) -> bool:
    """Delete video from S3"""
    try:
        s3_client.delete_object(Bucket=BUCKET_NAME, Key=s3_key)
        return True
    except Exception as e:
        print(f"Error deleting video from S3: {e}")
        return False