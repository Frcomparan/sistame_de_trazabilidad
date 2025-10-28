"""
API URLs for Events app.
"""
from django.urls import path
from .views import EventListView, EventTypeListView

urlpatterns = [
    path('', EventListView.as_view(), name='event-list'),
    path('types/', EventTypeListView.as_view(), name='event-type-list'),
]
