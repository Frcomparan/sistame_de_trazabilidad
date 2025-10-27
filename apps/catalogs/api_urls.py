"""
API URLs for Catalogs app.
"""
from django.urls import path
from .views import FieldListView, CampaignListView

urlpatterns = [
    path('fields/', FieldListView.as_view(), name='field-list'),
    path('campaigns/', CampaignListView.as_view(), name='campaign-list'),
]
