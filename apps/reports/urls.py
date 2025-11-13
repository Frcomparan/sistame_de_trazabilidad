"""
Web UI URLs for Reports app.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_dashboard_view, name='reports_dashboard'),
    path('trazabilidad/', views.traceability_report_view, name='traceability_report'),
    path('trazabilidad-campana/', views.campaign_traceability_report_view, name='campaign_traceability_report'),
    path('exportar/', views.export_events_view, name='export_events'),
]


