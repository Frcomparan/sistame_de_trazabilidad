"""
Web UI URLs for Catalogs app.
"""
from django.urls import path
from .views import (
    # Template views
    field_list_view, field_create_view, field_edit_view, field_delete_view,
    campaign_list_view, campaign_create_view, campaign_edit_view, campaign_delete_view,
    sensors_dashboard_view, sensors_data_api
)

urlpatterns = [
    # Template views - Fields
    path('fields/', field_list_view, name='field_list'),
    path('fields/create/', field_create_view, name='field_create'),
    path('fields/<uuid:pk>/edit/', field_edit_view, name='field_edit'),
    path('fields/<uuid:pk>/delete/', field_delete_view, name='field_delete'),
    
    # Template views - Campaigns
    path('campaigns/', campaign_list_view, name='campaign_list'),
    path('campaigns/create/', campaign_create_view, name='campaign_create'),
    path('campaigns/<uuid:pk>/edit/', campaign_edit_view, name='campaign_edit'),
    path('campaigns/<uuid:pk>/delete/', campaign_delete_view, name='campaign_delete'),
    
    # Sensors / IoT
    path('sensors/', sensors_dashboard_view, name='sensors_dashboard'),
    path('sensors/api/data/', sensors_data_api, name='sensors_data_api'),
]

