from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import VideoRecording
from video_handler import generate_presigned_upload_url, generate_presigned_view_url, delete_video_from_s3
import traceback

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_upload_url(request):
    """Get pre-signed URL for uploading video"""
    try:
        filename = request.data.get('filename', 'recording.webm')
        content_type = request.data.get('content_type', 'video/webm')
        
        upload_data = generate_presigned_upload_url(
            user_id=request.user.id,
            filename=filename,
            content_type=content_type
        )
        
        return Response(upload_data)
        
    except Exception as e:
        print(f"❌ Upload URL Error: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_video_metadata(request):
    """Save video metadata after successful upload"""
    try:
        video = VideoRecording.objects.create(
            user=request.user,
            title=request.data.get('title', ''),
            s3_key=request.data.get('s3_key'),
            s3_url=request.data.get('s3_url'),
            duration=request.data.get('duration'),
            file_size=request.data.get('file_size')
        )
        
        return Response({
            'id': video.id,
            'message': 'Video saved successfully'
        })
        
    except Exception as e:
        print(f"❌ Save Metadata Error: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_videos(request):
    """List all videos for current user"""
    try:
        videos = VideoRecording.objects.filter(user=request.user)
        
        video_list = []
        for video in videos:
            # Generate fresh pre-signed URL for viewing
            view_url = generate_presigned_view_url(video.s3_key)
            
            video_list.append({
                'id': video.id,
                'title': video.title,
                'view_url': view_url,
                'duration': video.duration,
                'file_size': video.file_size,
                'created_at': video.created_at.isoformat()
            })
        
        return Response(video_list)
        
    except Exception as e:
        print(f"❌ List Videos Error: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_video(request, video_id):
    """Delete a video"""
    try:
        video = VideoRecording.objects.get(id=video_id, user=request.user)
        
        # Delete from S3
        delete_video_from_s3(video.s3_key)
        
        # Delete from database
        video.delete()
        
        return Response({'message': 'Video deleted successfully'})
        
    except VideoRecording.DoesNotExist:
        return Response({'error': 'Video not found'}, status=404)
    except Exception as e:
        print(f"❌ Delete Video Error: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
    
