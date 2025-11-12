"""
API URLs for Events app.
"""
from django.urls import path
from .views import (
    EventListView, 
    EventTypeListView, 
    EventCreateView,
    EventDetailView,
    EventUpdateView,
    EventDeleteView,
    EventTypeDetailView,
    EventTypeUpdateView,
)

urlpatterns = [
    # Eventos
    path('', EventListView.as_view(), name='event-list'),
    path('create/', EventCreateView.as_view(), name='event-create'),
    path('<uuid:pk>/', EventDetailView.as_view(), name='event-detail'),
    path('<uuid:pk>/update/', EventUpdateView.as_view(), name='event-update'),
    path('<uuid:pk>/delete/', EventDeleteView.as_view(), name='event-delete'),
    
    # Tipos de Eventos
    path('types/', EventTypeListView.as_view(), name='event-type-list'),
    path('types/<uuid:pk>/', EventTypeDetailView.as_view(), name='event-type-detail'),
    path('types/<uuid:pk>/update/', EventTypeUpdateView.as_view(), name='event-type-update'),
]
