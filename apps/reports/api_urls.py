"""
API URLs for Reports app.
"""
from django.urls import path
from .views import (
    HealthCheckView,
    ReportTypesListView,
    FieldTraceabilityReportView,
    CampaignTraceabilityReportView
)

urlpatterns = [
    # Health check
    path('health/', HealthCheckView.as_view(), name='reports-health-check'),
    
    # Reportes disponibles
    path('types/', ReportTypesListView.as_view(), name='report-types-list'),
    
    # Generación de reportes
    path('field-traceability/', FieldTraceabilityReportView.as_view(), name='field-traceability-report'),
    path('campaign-traceability/', CampaignTraceabilityReportView.as_view(), name='campaign-traceability-report'),
]
