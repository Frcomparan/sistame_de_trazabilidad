"""
Web UI URLs for Core app.
"""
from django.urls import path
from .views import dashboard_view

urlpatterns = [
    # Dashboard view
    path('', dashboard_view, name='dashboard'),
]

