from django.urls import path
from . import views
from . import api_views
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Django template views
    path('', views.chat_view, name='chat'),
    path('ask/', views.ask_question, name='ask'),

    # Auth API endpoints
    path('api/auth/register/', api_views.register, name='register'),
    path('api/auth/login/', api_views.login, name='login'),
    path('api/auth/logout/', api_views.logout, name='logout'),
    path('api/auth/profile/', api_views.profile, name='profile'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

     # Chat history endpoints
    path('api/chat/history/', api_views.chat_history, name='chat_history'),
    path('api/chat/history/clear/', api_views.clear_chat_history, name='clear_history')
]