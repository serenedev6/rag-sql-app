from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UserSerializer
from .models import ChatHistory
from django_ratelimit.decorators  import ratelimit
from django.utils.decorators  import method_decorator


@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/m', method='POST', block=False)
def register(request):
    # Check if rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {
                'error': 'Too many registration attempts. Please try again in a minute.',
                'code': 'rate_limit_exceeded'
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response =  Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)

         # Set HttpOnly cookies
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=3600,
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite='Lax',
            max_age=604800,
        )

        return response
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def login(request):
    # Check if rate limited
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {
                'error': 'Too many login attempts. Please try again in a minute.',
                'code': 'rate_limit_exceeded'
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            'user': UserSerializer(user).data,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    
        # Set HttpOnly cookies
        response.set_cookie(
            key='access_token',
            value=access_token,
            httponly=True,
            secure=False,      # True in production
            samesite='Lax',
            max_age=3600       # 60 minutes
        )
        response.set_cookie(
            key='refresh_token',
            value=refresh_token,
            httponly=True,
            secure=False,      # True in Production
            samesite='Lax',
            max_age=604800     # 7 days
        )

        return response
    return Response(
        {'error': 'Invalid credentials'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    return Response(UserSerializer(request.user).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        # Blacklist refresh token
        refresh_token = request.data.get('refresh')
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()

        # Blacklist access token
        access_token = request.auth
        if access_token:
            from rest_framework_simplejwt.tokens import AccessToken
            from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
            from rest_framework_simplejwt.utils import datetime_from_epoch
            try:
                outstanding_token, _ = OutstandingToken.objects.get_or_create(
                    jti=access_token['jti'],
                    defaults={
                        'token': str(access_token),
                        'user': request.user,
                        'expires_at': datetime_from_epoch(access_token['exp']),
                    }
                )
                BlacklistedToken.objects.get_or_create(token=outstanding_token)
            except Exception as e:
                print(f"⚠️ Could not blacklist access token: {e}")

        response = Response({'message': 'Logged out successfully'})

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    user = request.user
    data = request.data

    if 'email' in data:
        user.email = data['email']
    if 'first_name' in data:
        user.first_name = data['first_name']
    if 'last_name' in data:
        user.last_name = data['last_name']

    user.save()
    return Response(UserSerializer(user).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def chat_history(request):
    history = ChatHistory.objects.filter(user=request.user)[:50]
    data = [
        {
            'id': h.id,
            'question': h.question,
            'answer': h.answer,
            'mode': h.mode,
            'created_at': h.created_at,
        }
        for h in history
    ]
    return Response(data)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def clear_chat_history(request):
    ChatHistory.objects.filter(user=request.user).delete()
    return Response({'message': 'Chat history cleared'})