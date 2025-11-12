"""
URL Configuration para el Sistema de Trazabilidad.
"""

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView, TemplateView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
import os

urlpatterns = [
    # Root redirect to login
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='root'),
    
    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # robots.txt
    path('robots.txt', lambda r: serve(r, 'robots.txt', document_root=settings.STATIC_ROOT or os.path.join(settings.BASE_DIR, 'static'))),
    
    # ========== WEB UI ROUTES (Templates/HTML) ==========
    path('dashboard/', include('apps.core.urls')),
    path('catalogs/', include('apps.catalogs.urls')),
    path('events/', include('apps.events.urls')),
    path('reportes/', include('apps.reports.urls')),  # Sistema de reportes
    
    # ========== API REST ROUTES (JSON) ==========
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints v1
    path('api/v1/auth/', include(('apps.core.api_urls', 'core-api'), namespace='core-api')),
    path('api/v1/catalogs/', include(('apps.catalogs.api_urls', 'catalogs-api'), namespace='catalogs-api')),
    path('api/v1/events/', include(('apps.events.api_urls', 'events-api'), namespace='events-api')),
    path('api/v1/reports/', include(('apps.reports.api_urls', 'reports-api'), namespace='reports-api')),
]

# Servir archivos media y static en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Personalización del admin
admin.site.site_header = "Sistema de Trazabilidad Agrícola"
admin.site.site_title = "Trazabilidad Admin"
admin.site.index_title = "Panel de Administración"
