from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UserSerializer
from .models import ChatHistory, EmailOTP
from django_ratelimit.decorators  import ratelimit
from django.utils.decorators  import method_decorator
from .email_utils import send_otp_email
from django.conf import settings
import logging
from .test_bedrock import test_bedrock

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def bedrock_test(request):
    """Test Bedrock integration directly"""
    result = test_bedrock()
    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def test_chat(request):
    print("🎯 TEST ENDPOINT HIT!")
    print(f"👤 User: {request.user}")
    print(f"📝 Data: {request.data}")
    return Response({
        'answer': 'Test successful!', 
        'user': str(request.user),
        'authenticated': request.user.is_authenticated
    })

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='3/m', method='POST', block=False)
def register(request):
    try:
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

            response = Response({
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
    
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return Response(
            {'error': f'Registration failed: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])  # TEMPORARY - remove after testing
def get_latest_otp(request):
    """TEMPORARY endpoint to retrieve OTP - DELETE AFTER TESTING"""
    email = request.query_params.get('email')
    if not email:
        return Response({'error': 'email parameter required'}, status=400)
    
    try:
        from django.contrib.auth.models import User
        user = User.objects.get(email=email)
        otp = EmailOTP.objects.filter(user=user).order_by('-created_at').first()
        
        if otp:
            return Response({
                'otp': otp.otp,
                'created_at': otp.created_at,
                'is_used': otp.is_used,
                'is_valid': otp.is_valid()
            })
        return Response({'error': 'No OTP found'}, status=404)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

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
        # Check if TOTP is enabled
        from .models import TOTPDevice
        try:
            totp_device = TOTPDevice.objects.get(user=user, is_enabled=True)
            totp_enabled = True
        except TOTPDevice.DoesNotExist:
            totp_enabled = False

        # Check if MFA is enabled (Email OTP or TOTP)
        if settings.MFA_ENABLED or totp_enabled:
            if totp_enabled:
                # TOTP is enabled - ask for TOTP code
                return Response({
                    'mfa_required': True,
                    'mfa_type': 'totp',
                    'user_id': user.id,
                    'message': 'Enter the code from your authenticator app'
                })
            else:
                # Email OTP
                if settings.MFA_ENABLED:
                    if not user.email:
                        return Response(
                            {'error': 'No email address associated with this account.'},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                # Generate and send OTP
                otp_obj = EmailOTP.generate_otp(user)
                send_otp_email(user.email, user.username, otp_obj.otp)

                return Response({
                    'mfa_required': True,
                    'user_id': user.id,
                    'message': f'OTP sent to {user.email[:3]}***@{user.email.split("@")[1]}'
                })

        # MFA disabled - return tokens directly
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

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def verify_totp_login(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {'error': 'Too many attempts. Please try again in a minute.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    user_id = request.data.get('user_id')
    token = request.data.get('token')

    if not user_id or not token:
        return Response(
            {'error': 'user_id and token are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from django.contrib.auth.models import User
        from .models import TOTPDevice
        user = User.objects.get(id=user_id)
        device = TOTPDevice.objects.get(user=user, is_enabled=True)

        if device.verify_token(token):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response = Response({
                'user': UserSerializer(user).data,
                'access': access_token,
                'refresh': refresh_token,
            })

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
        else:
            return Response(
                {'error': 'Invalid token. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except User.DoesNotExist:
        return Response({'error': 'Invalid user'}, status=status.HTTP_400_BAD_REQUEST)
    except TOTPDevice.DoesNotExist:
        return Response({'error': 'TOTP not enabled'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def verify_otp(request):
    was_limited = getattr(request, 'limited', False)
    if was_limited:
        return Response(
            {'error': 'Too many attempts. Please try again in a minute.'},
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )

    user_id = request.data.get('user_id')
    otp_code = request.data.get('otp')

    if not user_id or not otp_code:
        return Response(
            {'error': 'user_id and otp are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        from django.contrib.auth.models import User
        user = User.objects.get(id=user_id)
        otp_obj = EmailOTP.objects.filter(
            user=user,
            otp=otp_code,
            is_used=False
        ).latest('created_at')

        if not otp_obj.is_valid():
            return Response(
                {'error': 'OTP has expired. Please login again.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({
            'user': UserSerializer(user).data,
            'access': access_token,
            'refresh': refresh_token,
        })

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

    except User.DoesNotExist:
        return Response(
            {'error': 'Invalid user'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except EmailOTP.DoesNotExist:
        return Response(
            {'error': 'Invalid OTP'},
            status=status.HTTP_400_BAD_REQUEST
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


import pyotp
import qrcode
import base64
from io import BytesIO

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def totp_setup(request):
    """Generate TOTP secret and QR code for setup"""
    from .models import TOTPDevice

    # Get or create TOTP device
    device, created = TOTPDevice.objects.get_or_create(
        user=request.user,
        defaults={'secret_key': pyotp.random_base32()}
    )

    if not created and device.is_enabled:
        return Response(
            {'error': 'TOTP is already enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Generate new secret if not enabled yet
    if not device.is_enabled:
        device.secret_key = pyotp.random_base32()
        device.save()

    # Generate QR code
    qr_url = device.get_qr_code_url()
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return Response({
        'secret_key': device.secret_key,
        'qr_code': f'data:image/png;base64,{qr_base64}',
        'manual_entry': qr_url,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def totp_verify_setup(request):
    """Verify TOTP token and enable 2FA"""
    from .models import TOTPDevice

    token = request.data.get('token')
    if not token:
        return Response(
            {'error': 'Token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        device = TOTPDevice.objects.get(user=request.user)
        if device.verify_token(token):
            device.is_enabled = True
            device.save()
            return Response({'message': 'TOTP enabled successfully! ✅'})
        else:
            return Response(
                {'error': 'Invalid token. Please try again.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except TOTPDevice.DoesNotExist:
        return Response(
            {'error': 'Please setup TOTP first'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def totp_disable(request):
    """Disable TOTP"""
    from .models import TOTPDevice

    token = request.data.get('token')
    if not token:
        return Response(
            {'error': 'Token is required to disable TOTP'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        device = TOTPDevice.objects.get(user=request.user, is_enabled=True)
        if device.verify_token(token):
            device.delete()
            return Response({'message': 'TOTP disabled successfully'})
        else:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    except TOTPDevice.DoesNotExist:
        return Response(
            {'error': 'TOTP is not enabled'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def totp_status(request):
    """Check if TOTP is enabled for user"""
    from .models import TOTPDevice
    try:
        device = TOTPDevice.objects.get(user=request.user)
        return Response({
            'enabled': device.is_enabled,
        })
    except TOTPDevice.DoesNotExist:
        return Response({'enabled': False})
