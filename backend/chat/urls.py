from django.urls import path
from . import views
from . import api_views
from rest_framework_simplejwt.views import TokenRefreshView
from . import streaming_views  

urlpatterns = [
    # Django template views
    path('', views.chat_view, name='chat'),
    path('ask/', views.ask_question, name='ask'),

    # Auth API endpoints
    path('api/auth/register/', api_views.register, name='register'),
    path('api/auth/login/', api_views.login, name='login'),
    path('api/auth/logout/', api_views.logout, name='logout'),
    path('api/auth/profile/', api_views.profile, name='profile'),
    path('api/auth/profile/update/', api_views.update_profile, name='update_profile'),  # ← add this
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('debug/otp/', api_views.get_latest_otp, name='get_otp'),  # TEMPORARY

     # Chat history endpoints
    path('api/chat/history/', api_views.chat_history, name='chat_history'),
    path('api/chat/history/clear/', api_views.clear_chat_history, name='clear_history'),

    path('api/test-bedrock/', api_views.bedrock_test, name='bedrock_test'),


    # In urlpatterns list, add:
    path('ask-stream/', streaming_views.ask_stream, name='ask_stream'),
    path('ask-agent-stream/', streaming_views.ask_agent_stream, name='ask_agent_stream'),
    
    # Verify OTP
    path('api/auth/verify-otp/', api_views.verify_otp, name='verify_otp'),

    path('ask-agent/', views.ask_agent, name='ask_agent'),

    path('test-ask/', views.test_ask, name='test_ask'),
    path('api/test-chat/', api_views.test_chat, name='test_chat'),
    # Google Authenticator - TOTP
    path('api/auth/totp/setup/', api_views.totp_setup, name='totp_setup'),
    path('api/auth/totp/verify-setup/', api_views.totp_verify_setup, name='totp_verify_setup'),
    path('api/auth/totp/disable/', api_views.totp_disable, name='totp_disable'),
    path('api/auth/totp/status/', api_views.totp_status, name='totp_status'),
    path('api/auth/totp/verify-login/', api_views.verify_totp_login, name='verify_totp_login'),
]