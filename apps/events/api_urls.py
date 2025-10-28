"""
API URLs for Events app.
"""
from django.urls import path
from .views import EventListView, EventTypeListView, EventCreateView

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('create/', EventCreateView.as_view(), name='event-create'),
    path('types/', EventTypeListView.as_view(), name='event-type-list'),
]
