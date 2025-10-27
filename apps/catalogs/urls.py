from django.urls import path
from . import views

urlpatterns = [
    path('', views.FieldListView.as_view(), name='fields_list'),
]
