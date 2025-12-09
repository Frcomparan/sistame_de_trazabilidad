"""
API URLs for Catalogs app.
"""
from django.urls import path
from .views import (
    FieldListView, 
    CampaignListView,
    SensorDataAPIView,
    SensorChannelInfoAPIView,
)

urlpatterns = [
    path('fields/', FieldListView.as_view(), name='field-list'),
    path('campaigns/', CampaignListView.as_view(), name='campaign-list'),
    
    # Sensores IoT
    path('sensors/data/', SensorDataAPIView.as_view(), name='sensors-data'),
    path('sensors/channel/', SensorChannelInfoAPIView.as_view(), name='sensors-channel-info'),
]
