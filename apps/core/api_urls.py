"""
API URLs for Core app (Authentication).
"""
from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView

urlpatterns = [
    # JWT Token endpoints
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),
]
