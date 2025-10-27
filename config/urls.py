"""
URL Configuration para el Sistema de Trazabilidad.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints
    path('api/v1/auth/', include('apps.core.urls')),
    path('api/v1/catalogs/', include('apps.catalogs.urls')),
    path('api/v1/events/', include('apps.events.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "Sistema de Trazabilidad Agrícola"
admin.site.site_title = "Trazabilidad Admin"
admin.site.index_title = "Panel de Administración"
