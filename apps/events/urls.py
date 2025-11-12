"""
Web UI URLs for Events app.
"""
from django.urls import path
from .views import (
    event_list_view,
    event_create_view,
    event_detail_view,
    get_event_type_info,
    event_type_list_view,
    event_type_create_view,
    event_type_edit_view,
    event_type_delete_view,
)

urlpatterns = [
    # Event URLs
    path('', event_list_view, name='event_list'),
    path('create/', event_create_view, name='event_create'),
    path('<uuid:pk>/', event_detail_view, name='event_detail'),
    path('api/event-type/<int:pk>/info/', get_event_type_info, name='event_type_info'),
    
    # Event Type URLs
    path('types/', event_type_list_view, name='event_type_list'),
    path('types/create/', event_type_create_view, name='event_type_create'),
    path('types/<int:pk>/edit/', event_type_edit_view, name='event_type_edit'),
    path('types/<int:pk>/delete/', event_type_delete_view, name='event_type_delete'),
]

