"""
URL Configuration para el Sistema de Trazabilidad.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Root redirect to login
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='root'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard
    path('dashboard/', include('apps.core.urls')),
    
    # Catalogs Web UI
    path('catalogs/', include('apps.catalogs.urls')),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints
    path('api/v1/auth/', include('apps.core.urls')),
    path('api/v1/catalogs/', include(('apps.catalogs.api_urls', 'catalogs-api'), namespace='catalogs-api')),
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
